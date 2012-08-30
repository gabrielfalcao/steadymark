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

version = '0.2.0'

import re
import os
import sys
import traceback
import codecs
from doctest import (
    DocTestParser,
    Example,
    DocTest,
    DocTestRunner,
    TestResults,
)
from datetime import datetime


from misaka import (
    BaseRenderer,
    Markdown,
    EXT_FENCED_CODE,
    EXT_NO_INTRA_EMPHASIS,
)


class MarkdownTest(object):
    def __init__(self, title, raw_code):
        self.title = title
        self.raw_code = raw_code

        globs = globals()
        dt_parser = DocTestParser()
        doctests = filter(
            lambda item: isinstance(item, Example),
            dt_parser.parse(raw_code),
        )
        if any(doctests):
            self.code = DocTest(
                examples=doctests,
                globs=globs,
                name=title,
                filename=None,
                lineno=None,
                docstring=None)
        else:
            self.code = compile(raw_code, "@STEADYMARK@", "exec")

    def run(self):
        before = datetime.now()
        failure = None
        if isinstance(self.code, DocTest):
            runner = DocTestRunner()
            result = runner.run(self.code)
            after = datetime.now()
            return result, before, after
        else:
            try:
                eval(self.code)
            except:
                failure = sys.exc_info()

        after = datetime.now()

        return failure, before, after


class SteadyMark(BaseRenderer):
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

    def postprocess(self, full_document):
        tests = []

        for test in filter(lambda x: 'code' in x, self._tests):
            raw_code = str(test['code'].encode('utf-8'))
            title = str(test['title'].encode('utf-8'))
            tests.append(MarkdownTest(title, raw_code))

        self.tests = tests

    @classmethod
    def inspect(cls, markdown):
        renderer = cls()
        extensions = EXT_FENCED_CODE | EXT_NO_INTRA_EMPHASIS
        md = Markdown(renderer, extensions=extensions)
        md.render(markdown)
        return renderer

    def run(self):
        for test in self.tests:
            test.run()


class Runner(object):
    def __init__(self, filename=None, text=u''):
        if filename and not os.path.exists(filename):
            print 'steadymark could not find {0}'.format(filename)
            sys.exit(1)

        if filename:
            raw_md = codecs.open(filename, 'rb', 'utf-8').read()
            text = unicode(raw_md)

        self.steadymark = SteadyMark.inspect(text)
        self.filename = filename
        self.text = text

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

    def format_traceback(self, title, failure):
        exc, exc_instance, tb = failure

        formatted_tb = traceback.format_exc(exc_instance).strip()
        if 'None' == formatted_tb:
            formatted_tb = ''.join(traceback.format_tb(tb))
            formatted_tb = formatted_tb.replace(
                u'File "@STEADYMARK@',
                u'In the test "@STEADYMARK@',
            )
            formatted_tb = formatted_tb.replace(
                u'@STEADYMARK@', unicode(title))

        return u'{0} {1}\n{2}'.format(
            exc.__name__,
            exc_instance,
            formatted_tb,
        )

    def report_doctest_result(self, test, result, before, after):
        # shift = before - after
        # ms = self.format_ms(shift.microseconds / 1000)
        # import ipdb;ipdb.set_trace()
        pass

    def report_raw_test_result(self, test, failure, before, after):
        shift = before - after
        ms = self.format_ms(shift.microseconds / 1000)
        lines = test.raw_code.splitlines()

        if not failure:
            return self.print_green('\xe2\x9c\x93 {0}'.format(ms))

        self.print_red('\xe2\x9c\x97 {0}'.format(ms))
        exc, exc_instance, tb = failure

        formatted_tb = self.format_traceback(test.title, failure)

        tb = tb.tb_next
        if tb:
            line = lines[tb.tb_lineno - 1]
            self.print_red("{0}     {1}".format(formatted_tb, line))
        elif issubclass(exc, SyntaxError):
            self.print_red(formatted_tb, indentation=2)

    def run(self):
        if self.filename:
            print "Running tests from {0}".format(self.filename)

        for test in self.steadymark.tests:
            sys.stdout.write("{0} ".format(test.title))
            result, before, after = test.run()
            if isinstance(result, TestResults):
                self.report_doctest_result(test, result, before, after)
            else:
                self.report_raw_test_result(test, result, before, after)

        return self.steadymark


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
