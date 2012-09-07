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

version = '0.4.1'

import re
import os
import sys
import traceback
import codecs
from doctest import (
    DocTestParser,
    DocTest,
    DebugRunner,
    DocTestFailure,
)
from datetime import datetime
try:
    from couleur import SUPPORTS_ANSI
except ImportError:
    SUPPORTS_ANSI = False

from misaka import (
    BaseRenderer,
    Markdown,
    EXT_FENCED_CODE,
    EXT_NO_INTRA_EMPHASIS,
)


class SteadyMarkDoctestRunner(DebugRunner):
    def report_unexpected_exception(self, out, test, example, exc_info):
        exc_type, exc_val, tb = exc_info
        if exc_type is DocTestFailure:
            raise exc_info
        raise exc_val


class MarkdownTest(object):
    def __init__(self, title, raw_code, globs, locs):
        self.title = title
        self.raw_code = raw_code

        self.globs = globs
        self.locs = locs
        dt_parser = DocTestParser()
        doctests = dt_parser.get_examples(raw_code)

        if any(doctests):
            self.code = DocTest(
                examples=doctests,
                globs=self.globs,
                name=title,
                filename=None,
                lineno=None,
                docstring=None)
        else:
            self.code = compile(raw_code, title, "exec")

    def _run_raw(self):
        return eval(self.code, self.globs, self.locs)

    def _run_doctest(self):
        if not isinstance(self.code, DocTest):
            raise TypeError(
                "Attempt to run a non-doctest as doctest: %r" % self.code)

        runner = SteadyMarkDoctestRunner(verbose=False)
        return runner.run(self.code)

    def run(self):
        before = datetime.now()
        failure = None
        result = None

        is_doctest = isinstance(self.code, DocTest)
        try:
            if is_doctest:
                result = self._run_doctest()
            else:
                result = self._run_raw()

        except:
            failure = sys.exc_info()

        after = datetime.now()

        return result, failure, before, after


class SteadyMark(BaseRenderer):
    title_regex = re.compile(ur'(?P<title>[^#]+)(?:[#]+(?P<index>\d+))?')

    def preprocess(self, text):
        self._tests = [{}]
        return unicode(text)

    def block_code(self, code, language):
        if language != 'python':
            return

        if re.match('^#\s*steadymark:\s*ignore', code):
            return

        item = self._tests[-1]
        if 'code' in item:  # the same title has more than 1 code
            found = self.title_regex.search(item['title'])
            title = found.group('title').rstrip()
            index = int(found.group('index') or 0)

            if not index:
                index = 1
                item['title'] = '{0} #{1}'.format(title, index)

            new_item = {
                'title': '{0} #{1}'.format(title, index + 1),
                'level': item['level'],
                'code': code,
            }

            self._tests.append(new_item)
            item = self._tests[-1]

        else:
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
            u'level': int(level),
        })

    def postprocess(self, full_document):
        tests = []

        globs = globals()
        locs = locals()
        for test in filter(lambda x: 'code' in x, self._tests):
            raw_code = str(test['code'].encode('utf-8'))
            title = str(test['title'].encode('utf-8'))
            tests.append(MarkdownTest(title, raw_code, globs=globs, locs=locs))

        self.tests = tests

    @classmethod
    def inspect(cls, markdown):
        renderer = cls()
        extensions = EXT_FENCED_CODE | EXT_NO_INTRA_EMPHASIS
        md = Markdown(renderer, extensions=extensions)
        md.render(markdown)
        return renderer


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

    def print_white(self, text, indentation=0):
        white = {
            True: u'\033[1;37m',
            False: u'',
        }
        for line in text.splitlines():
            print "{1}{2}{0}\033[0m".format(
                line, ' ' * indentation, white[SUPPORTS_ANSI])

    def __getattr__(self, attr):
        if attr not in (
            'print_white',
            'print_green',
            'print_red',
            'print_yellow',
        ):
            return super(Runner, self).__getattribute__(attr)

        color_for = {
            'print_white': u'\033[1;37m',
            'print_red': u'\033[1;31m',
            'print_green': u'\033[1;32m',
            'print_yellow': u'\033[1;33m',
        }
        ansi = color_for[attr]
        if SUPPORTS_ANSI:
            color = ansi
            no_color = '\033[0m'
        else:
            no_color = color = ''

        def printer(text, indentation=0):
            for line in text.splitlines():
                print "{1}{2}{0}{3}".format(
                    line, ' ' * indentation, color, no_color)

        return printer

    def format_ms(self, ms):
        ms = int(ms)
        base = '{0}ms'.format(ms)
        if SUPPORTS_ANSI:
            return "\033[1;33m{0}\033[0m".format(base)
        else:
            return base

    def format_traceback(self, test, failure):
        exc, exc_instance, tb = failure
        # formatted_tb = traceback.format_exc(exc_instance).strip()
        # if 'None' == formatted_tb:
        formatted_tb = ''.join(traceback.format_tb(tb))
        formatted_tb = formatted_tb.replace(
            u'File "{0}"'.format(test.title),
            u'In the test "{0}"'.format(test.title),
        )
        formatted_tb = formatted_tb.replace(
            u'@STEADYMARK@', unicode(test.title))

        if SUPPORTS_ANSI:
            color = '\033[1;36m'
        else:
            color = ''
        return u'{0} {3}{1}\n{2}\n'.format(
            exc.__name__,
            exc_instance,
            formatted_tb,
            color,
        )

    def report_success(self, test, shift, ms):
        self.print_green('\xe2\x9c\x93 {0}'.format(ms))
        print

    def report_failure(self, test, failure, shift, ms):
        self.print_red('\xe2\x9c\x97 {0}'.format(ms))
        exc_type, exc_val, exc_tb = failure

        if exc_type is DocTestFailure:
            formatted_tb = u"the line {0}: {1}\n".format(
                exc_val.example.lineno,
                exc_val.example.source,
            )
            if exc_val.example.exc_msg:
                formatted_tb += "{0}\n".format(
                    exc_val.example.exc_msg)
            else:
                formatted_tb += ("resulted in:\n{0}\n"
                                 "when expecting:\n{1}\n".format(
                                     exc_val.got, exc_val.example.want))

        else:
            formatted_tb = self.format_traceback(test, failure)

        self.print_red(formatted_tb, indentation=2)

        header = "original code:"
        header_length = len(header)
        self.print_white("*" * header_length)
        self.print_white(header)
        self.print_white("*" * header_length)

        self.print_yellow(test.raw_code, indentation=2)
        print

    def report_test_result(self, test, failure, before, after):
        shift = before - after
        ms = self.format_ms(shift.microseconds / 1000)

        if not failure:
            return self.report_success(test, shift, ms)

        return self.report_failure(test, failure, shift, ms)

    def run(self):
        if self.filename:
            print "Running tests from {0}".format(self.filename)

        exit_status = 0
        for test in self.steadymark.tests:
            title = "{0} ".format(test.title)
            title_length = len(title)
            print "." * title_length
            sys.stdout.write(title)
            result, failure, before, after = test.run()
            if failure:
                exit_status = 1
            self.report_test_result(test, failure, before, after)

        if exit_status is not 0:
            sys.exit(exit_status)

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
