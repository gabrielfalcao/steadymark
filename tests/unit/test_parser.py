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
from sure import this
from steadymark.core import SteadyMark


def test_find_python_code_with_titles():
    (u"SteadyMark should find python code and use the "
     "previous header as title")

    md = u"""# test 1
a paragraph

```python
assert False, 'boom!'
```

# not a test

foobar

```ruby
ruby no!
```

# another part

## test 2

a paragraph

```python
assert False, 'uh yeah'
```
    """

    sm = SteadyMark.inspect(md)

    sm.tests.should.have.length_of(2)

    test1, test2 = sm.tests

    test1.title.should.equal("test 1")
    test1.raw_code.should.equal("assert False, 'boom!'")
    eval.when.called_with(test1.code).should.throw(AssertionError, "boom!")

    test2.title.should.equal("test 2")
    test2.raw_code.should.equal("assert False, 'uh yeah'")
    eval.when.called_with(test2.code).should.throw(AssertionError, "uh yeah")


def test_find_inline_doctests_with_titles():
    (u"SteadyMark should find docstrings and use the "
     "previous header as title")

    md = u"""# test 1
a paragraph

```python
>>> x = 'doc'
>>> y = 'test'
>>> assert (x + y) == 'doctest'
```

# not a test

foobar

```ruby
ruby no!
```

# another part

## test 2

a paragraph

```python
assert False, 'uh yeah'
```
    """

    sm = SteadyMark.inspect(md)

    sm.tests.should.have.length_of(2)

    test1, test2 = sm.tests

    test1.title.should.equal("test 1")
    test1.raw_code.should.equal(">>> x = 'doc'\n"
                                ">>> y = 'test'\n"
                                ">>> assert (x + y) == 'doctest'")

    this(test1.code).should.be.a('doctest.DocTest')
    test1.run()
    test2.title.should.equal("test 2")
    test2.raw_code.should.equal("assert False, 'uh yeah'")
    eval.when.called_with(test2.code).should.throw(AssertionError, "uh yeah")


def test_use_same_title_for_all_tests():
    (u"SteadyMark should find all the tests under the same header (title)")

    md = u"""# Test Foo
a paragraph

```python
assert False, 'FIRST'
```

```python
assert False, 'SECOND'
```

```python
assert False, 'THIRD'
```

    """

    sm = SteadyMark.inspect(md)

    sm.tests.should.have.length_of(3)

    test1, test2, test3 = sm.tests

    test1.title.should.equal("Test Foo #1")
    eval.when.called_with(test1.code).should.throw(AssertionError, "FIRST")

    test2.title.should.equal("Test Foo #2")
    eval.when.called_with(test2.code).should.throw(AssertionError, "SECOND")

    test3.title.should.equal("Test Foo #3")
    eval.when.called_with(test3.code).should.throw(AssertionError, "THIRD")


def test_skip_tests_marked_with_ignore():
    (u"SteadyMark should skip tests with the 'ignore' modeline")

    md = u"""# My test
```python
# steadymark: ignore
This should break, but it won't because steady mark will ignore this
```

# Another test
```python
>>> 1 + 1
2
```
"""
    sm = SteadyMark.inspect(md)
    sm.tests.should.have.length_of(1)
    sm.tests[0].title.should.be.equal('Another test')
