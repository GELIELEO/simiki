#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, with_statement, unicode_literals

import os
import os.path
import unittest
import datetime
import shutil

from simiki.config import parse_config, get_default_config
from simiki.utils import copytree
from simiki.generators import PageGenerator
from simiki.compat import unicode

test_path = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.dirname(test_path)


class TestPageGenerator(unittest.TestCase):
    def setUp(self):
        self.wiki_path = os.path.join(test_path, 'mywiki_for_generator')

        os.chdir(self.wiki_path)

        self.config_file = os.path.join(base_path, 'simiki',
                                        'conf_templates', '_config.yml.in')

        self.config = parse_config(self.config_file)

        s_themes_path = os.path.join(base_path, 'simiki', 'themes')
        self.d_themes_path = os.path.join('./', 'themes')
        if os.path.exists(self.d_themes_path):
            shutil.rmtree(self.d_themes_path)
        copytree(s_themes_path, self.d_themes_path)

        self.generator = PageGenerator(self.config, self.wiki_path)

    def test_get_category_and_file(self):
        src_file = os.path.join(self.wiki_path, 'content', 'foo目录',
                                'foo_page_中文.md')
        self.generator.src_file = src_file
        category, filename = self.generator.get_category_and_file()
        self.assertEqual(
            (category, filename),
            (u'foo\u76ee\u5f55', u'foo_page_\u4e2d\u6587.md')
        )

    def test_get_meta_and_content(self):
        src_file = os.path.join(self.wiki_path, 'content', 'foo目录',
                                'foo_page_中文.md')
        self.generator.src_file = src_file
        meta, content = self.generator.get_meta_and_content()
        expected_meta = {'date': '2013-10-17 00:03', 'layout': 'page',
                         'title': 'Foo Page 2'}
        self.assertEqual(meta, expected_meta)
        self.assertEqual(content, '<p>Simiki is a simple wiki '
                                  'framework, written in Python.</p>')

        # get meta notaion error
        src_file = os.path.join(self.wiki_path, 'content', 'foo目录',
                                'foo_page_中文_meta_error_1.md')
        self.generator.src_file = src_file
        self.assertRaises(Exception, self.generator.get_meta_and_content)

        src_file = os.path.join(self.wiki_path, 'content', 'foo目录',
                                'foo_page_中文_meta_error_2.md')
        self.generator.src_file = src_file
        self.assertRaises(Exception, self.generator.get_meta_and_content)

    def test_get_template_vars(self):
        src_file = os.path.join(self.wiki_path, 'content', 'foo目录',
                                'foo_page_中文.md')
        self.generator.src_file = src_file
        meta, content = self.generator.get_meta_and_content()
        template_vars = self.generator.get_template_vars(meta, content)
        expected_template_vars = {
            u'page': {
                u'category': u'foo\u76ee\u5f55',
                u'content': u'<p>Simiki is a simple wiki '
                            'framework, written in Python.</p>',
                u'filename': u'foo_page_\u4e2d\u6587.html',
                u'date': '2013-10-17 00:03',
                u'layout': 'page',
                u'title': 'Foo Page 2'
            },
            u'site': get_default_config()
        }

        expected_template_vars['site'].update({'root': ''})
        template_vars['site'].pop('time')
        expected_template_vars['site'].pop('time')
        assert template_vars == expected_template_vars

    def test_to_html(self):
        src_file = os.path.join(self.wiki_path, 'content', 'foo目录',
                                'foo_page_中文.md')
        html = self.generator.to_html(src_file).strip()
        expected_output = os.path.join(self.wiki_path, 'expected_output.html')
        fd = open(expected_output, "rb")
        year = datetime.date.today().year
        expected_html = unicode(fd.read(), "utf-8") % year
        assert html == expected_html

        # load template error
        src_file = os.path.join(self.wiki_path, 'content', 'foo目录',
                                'foo_page_中文.md')
        self.assertRaises(Exception, PageGenerator, self.config,
                          'wrong_basepath', src_file)

    def test_get_layout(self):
        src_file = os.path.join(self.wiki_path, 'content', 'foo目录',
                                'foo_page_layout_old_post.md')
        self.generator.src_file = src_file
        meta, _ = self.generator.get_meta_and_content()

        layout = self.generator.get_layout(meta)
        self.assertEqual(layout, 'page')

        src_file = os.path.join(self.wiki_path, 'content', 'foo目录',
                                'foo_page_layout_without_layout.md')
        self.generator.src_file = src_file
        meta, _ = self.generator.get_meta_and_content()

        layout = self.generator.get_layout(meta)
        self.assertEqual(layout, 'page')

    def test_get_meta(self):
        src_file = os.path.join(self.wiki_path, 'content', 'foo目录',
                                'foo_page_get_meta_yaml_error.md')
        self.generator.src_file = src_file
        self.assertRaises(Exception, self.generator.get_meta_and_content)

        src_file = os.path.join(self.wiki_path, 'content', 'foo目录',
                                'foo_page_get_meta_without_title.md')
        self.generator.src_file = src_file
        self.assertRaises(Exception, self.generator.get_meta_and_content)

    def tearDown(self):
        if os.path.exists(self.d_themes_path):
            shutil.rmtree(self.d_themes_path)


if __name__ == "__main__":
    unittest.main()
