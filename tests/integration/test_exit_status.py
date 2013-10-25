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
import os
import sys
from os.path import dirname, abspath, join
from subprocess import check_call, CalledProcessError


CURDIR = abspath(join(dirname(__file__)))
MAINDIR = abspath(join(CURDIR, '..', '..'))

main_file = join(MAINDIR, 'steadymark', '__init__.py')


def run(path, *args):
    params = [sys.executable, main_file] + list(args) + [path]
    out = open(os.devnull, 'w')
    return check_call(params, stdout=out, stderr=out)


def test_failure_exits_with_1():
    (u"SteadyMark should exit with status 1 in case of failure")

    path = join(CURDIR, 'fails.md')
    run.when.called_with(path).should.throw(
                CalledProcessError, 'exit status 1')


def test_success_exits_with_0():
    (u"SteadyMark should exit with status 0 in case of success")

    status = run(join(CURDIR, 'passes.md'))
    status.should.equal(0)


def test_import_boot_file():
    (u"SteadyMark should be able to import a python file before running the tests")

    path = join(CURDIR, 'passes.md')
    run.when.called_with(path, "-b", join(CURDIR, 'firstboot.py')).should.throw(
                CalledProcessError, 'exit status 42')
