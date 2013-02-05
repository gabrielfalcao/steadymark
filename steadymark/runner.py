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
from __future__ import unicode_literals

import os
import sys
import traceback
import codecs

try:
    from couleur import SUPPORTS_ANSI
except ImportError:
    SUPPORTS_ANSI = False

from steadymark.core import (
    SteadyMark,
    DocTestFailure,
)
from steadymark.six import text_type, PY3

if not PY3:
    # We do this so that redirecting to pipes will work
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)


class Runner(object):
    def __init__(self, filename=None, text=u''):
        if filename and not os.path.exists(filename):
            print('steadymark could not find {0}'.format(filename))
            sys.exit(1)

        if filename:
            raw_md = codecs.open(filename, 'rb', 'utf-8').read()
            text = text_type(raw_md)

        self.steadymark = SteadyMark.inspect(text)
        self.filename = filename
        self.text = text

    def print_white(self, text, indentation=0):
        white = {
            True: u'\033[1;37m',
            False: u'',
        }
        for line in text.splitlines():
            print("{1}{2}{0}\033[0m".format(
                line, ' ' * indentation, white[SUPPORTS_ANSI]))

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
                print("{1}{2}{0}{3}".format(
                    line, ' ' * indentation, color, no_color))

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
            u'@STEADYMARK@', text_type(test.title))

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
        self.print_green('\u2714 {0}'.format(ms))
        print

    def report_failure(self, test, failure, shift, ms):
        self.print_red('\u2718 {0}'.format(ms))
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
            print("Running tests from {0}".format(self.filename))

        exit_status = 0
        for test in self.steadymark.tests:
            title = "{0} ".format(test.title)
            title_length = len(title)
            print("." * title_length)
            sys.stdout.write(title)
            result, failure, before, after = test.run()
            if failure:
                exit_status = 1
            self.report_test_result(test, failure, before, after)

        if exit_status is not 0:
            sys.exit(exit_status)

        return self.steadymark
