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

version = '0.1.4'
import re
import os
import sys
import traceback
import codecs
from datetime import datetime

from misaka import (
    BaseRenderer,
    Markdown,
    EXT_FENCED_CODE,
    EXT_NO_INTRA_EMPHASIS,
)


class READMETestRunner(BaseRenderer):
    filename = None

    def preprocess(self, text):
        self._tests = [{}]
        return unicode(text)

    def block_code(self, code, language):
        if language != 'python':
            return

        item = self._tests[-1]
        item[u'code'] = unicode(code).strip()
        if 'title' not in item:
            item[u'title'] = u'Test #{0}'.format(len(self._tests))
            self._tests.append({})

    def header(self, title, level):
        t = unicode(title)
        t = re.sub(ur'^[# ]*(.*)', '\g<1>', t)
        t = re.sub(ur'`([^`]*)`', '\033[1;33m\g<1>\033[0m', t)
        self._tests.append({
            u'title': t,
        })

    def print_red(self, text, indentation=0):
        for line in text.splitlines():
            print "{1}\033[1;31m{0}\033[0m".format(line, ' ' * indentation)

    def print_green(self, text, indentation=0):
        for line in text.splitlines():
            print "{1}\033[1;32m{0}\033[0m".format(line, ' ' * indentation)

    def format_ms(self, ms):
        ms = int(ms)
        if ms < 1000:
            return ""

        return "\033[1;33m{0}ms\033[0m".format(ms)

    @property
    def tests(self):
        return [t for t in self._tests if 'code' in t]

    def postprocess(self, full_document):
        if not self.filename:
            return full_document

        actual_tests = self.tests
        if actual_tests:
            print "Running code snippets from {0}\n".format(self.filename)
        else:
            print "No tests found in {0}".format(self.filename)

        failed = False
        for test in actual_tests:
            raw_code = str(test['code'].encode('utf-8'))
            title = str(test['title'].encode('utf-8'))
            sys.stdout.write("{0} ".format(title))
            before = datetime.now()
            failure = None
            lines = raw_code.splitlines()

            try:
                code = compile(raw_code, "@STEADYMARK@", "exec")
                eval(code)
            except:
                failure = sys.exc_info()
                failed = True
            after = datetime.now()

            shift = before - after
            ms = shift.microseconds / 1000
            if not failure:
                self.print_green('\xe2\x9c\x93 {0}'.format(self.format_ms(ms)))
            else:
                self.print_red('\xe2\x9c\x97 {0}'.format(self.format_ms(ms)))
                exc, exc_instance, tb = failure
                tb = tb.tb_next
                formatted_tb = self.format_traceback(title, exc_instance)

                if tb:
                    line = lines[tb.tb_lineno - 1]
                    self.print_red("{0}     {1}".format(formatted_tb, line))
                elif issubclass(exc, SyntaxError):
                    self.print_red(formatted_tb, indentation=2)

        sys.exit(int(failed))

    def format_traceback(self, title, exception):
        formatted_tb = traceback.format_exc(exception)
        formatted_tb = formatted_tb.replace(
            'File "@STEADYMARK@',
            'In the test "@STEADYMARK@',
        )
        return formatted_tb.replace(
            '@STEADYMARK@', title)

class Runner(object):
    def __init__(self, filename=None, text=u''):
        renderer = READMETestRunner()
        renderer.filename = filename
        extensions = EXT_FENCED_CODE | EXT_NO_INTRA_EMPHASIS

        if filename and not os.path.exists(renderer.filename):
            print 'steadymark could not find {0}'.format(renderer.filename)
            sys.exit(1)

        if filename:
            raw_md = codecs.open(renderer.filename, 'rb', 'utf-8').read()
            text = unicode(raw_md)

        self.text = text
        self.md = Markdown(renderer, extensions=extensions)
        self.renderer = renderer

    def run(self):
        renderer = self.renderer
        return self.md.render(self.text) and renderer or renderer


def main():
    from optparse import OptionParser

    parser = OptionParser()
    (options, args) = parser.parse_args()
    args = args or ['README.md']

    for filename in args:
        runner = Runner(filename)
        runner.run()

if __name__ == '__main__':
    main()
