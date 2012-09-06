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
from steadymark import SteadyMark


def test_find_doctest_code_with_titles():
    (u"SteadyMark should find doctest and use the "
     "previous header as title")

    md = u"""# test 1
a paragraph

```python
>>> raise TypeError('boom')
```
    """

    sm = SteadyMark.inspect(md)
    test1 = sm.tests[0]
    result, (_, failure, tb), before, after = test1.run()

    test1.title.should.equal("test 1")
    failure.should.be.a(TypeError)
    "boom".should.be.within(unicode(failure))


def test_find_python_code_with_titles():
    (u"SteadyMark should find python code and use the "
     "previous header as title")

    md = u"""# test 1
a paragraph

```python
raise ValueError('boom')
```
    """

    sm = SteadyMark.inspect(md)
    test1 = sm.tests[0]
    result, (_, failure, tb), before, after = test1.run()

    test1.title.should.equal("test 1")
    failure.should.be.a(ValueError)
    "boom".should.be.within(unicode(failure))


def test_keeps_scope_from_test_to_test():
    (u"SteadyMark should accumulate the scope throughout the python code snippets")

    md = u"""# test 1
a paragraph

```python
value = "YAY"
```

# test 2
a paragraph

```python
assert value == 'YAY'
```
"""

    sm = SteadyMark.inspect(md)
    test1, test2 = sm.tests
    result1, failure1, before, after = test1.run()
    result2, failure2, before, after = test2.run()

    test1.title.should.equal("test 1")
    test2.title.should.equal("test 2")

    failure1.should.be.none
    failure2.should.be.none
