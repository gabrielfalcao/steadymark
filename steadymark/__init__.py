#!/usr/bin/env python
# -*- coding: utf-8 -*-
# <steadymark - markdown-based test runner for python>
# Copyright (C) <2012>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

version = '0.1.3'

import os
import sys
import traceback
from datetime import datetime

from misaka import (
    BaseRenderer,
    Markdown,
    EXT_FENCED_CODE,
    EXT_NO_INTRA_EMPHASIS,
)


class READMETestRunner(BaseRenderer):
    tests = [{}]
    filename = None

    def block_code(self, code, language):
        if language != 'python':
            return

        item = self.tests[-1]
        item[u'code'] = unicode(code)
        if 'title' not in item:
            item[u'title'] = u'Test #{0}'.format(len(self.tests))
            self.tests.append({})

    def header(self, title, level):
        self.tests.append({
            u'title': unicode(title),
        })

    def print_red(self, text):
        print "\033[1;31m{0}\033[0m".format(text)

    def print_green(self, text):
        print "\033[1;32m{0}\033[0m".format(text)

    def format_ms(self, ms):
        ms = int(ms)
        if ms < 1000:
            return ""

        return "\033[1;33m{0}ms\033[0m".format(ms)

    def postprocess(self, full_document):
        actual_tests = [t for t in self.tests if 'code' in t]
        if actual_tests:
            print "Running code snippets from {0}\n".format(self.filename)
        else:
            print "No tests found in {0}".format(self.filename)

        failed = False
        for test in actual_tests:
            sys.stdout.write("{0} ".format(test['title']))
            before = datetime.now()
            failure = None
            lines = test['code'].splitlines()
            try:
                code = compile(test['code'], "README.md", "exec")
                eval(code)
            except Exception:
                failure = sys.exc_info()

            after = datetime.now()

            shift = before - after
            ms = shift.microseconds / 1000
            if not failure:
                self.print_green('\xe2\x9c\x93 {0}'.format(self.format_ms(ms)))
            else:
                self.print_red('\xe2\x9c\x97 {0}'.format(self.format_ms(ms)))
                failed = True
                exc, name, tb = failure
                tb = tb.tb_next
                line = lines[tb.tb_lineno - 1]
                self.print_red("Traceback (most recent call last):")
                formatted_tb = traceback.format_tb(tb)[-1]
                self.print_red("{0}     {1}".format(formatted_tb, line))

        sys.exit(int(failed))


def main():
    from optparse import OptionParser

    parser = OptionParser()
    (options, args) = parser.parse_args()
    args = args or ['README.md']

    for filename in args:
        renderer = READMETestRunner()
        renderer.filename = filename

        extensions = EXT_FENCED_CODE | EXT_NO_INTRA_EMPHASIS
        md = Markdown(renderer, extensions=extensions)
        if not os.path.exists(renderer.filename):
            print 'steadymark could not find {0}'.format(renderer.filename)
            sys.exit(1)
        text = open(renderer.filename).read()
        md.render(text)


if __name__ == '__main__':
    main()
