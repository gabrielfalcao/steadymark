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
import imp
from optparse import OptionParser
from steadymark.six import text_type
from steadymark.version import version
from steadymark.runner import Runner


def run(filenames):
    for filename in filenames:
        runner = Runner(filename)
        runner.run()


def main():
    parser = OptionParser()
    parser.add_option("-b", "--bootstrap", dest="bootstrap_file",
                  help="A path to a python file to be loaded before steadymark runs the tests")

    (options, args) = parser.parse_args()

    if options.bootstrap_file:
        imp.load_source('steadymark_bootstrap', options.bootstrap_file)

    run(args or ['README.md'])

__all__ = [
    'run',
    'Runner',
    'version',
]

if __name__ == '__main__':
    main()
