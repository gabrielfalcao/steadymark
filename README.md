# Steady Mark
> version 0.1.4
[![Build Status](https://secure.travis-ci.org/gabrielfalcao/steadymark.png?branch=master)](http://travis-ci.org/#!/gabrielfalcao/steadymark)

# Turning your github readme files into python test suites since 2012

Steady Mark was created for python developers that love Github and
markdown.

## How it works:

Write your documentation using [github-flavored markdown](http://github.github.com/github-flavored-markdown/), surround your
snippets with python code blocks and steadymark will automatically
find and run them, if there is a header preceeding your python snippet
it will be used as title for your test.

# Advantages:

* Add test coverage to your app/library while documenting it
* Never have old malfunctional examples on your project's main page in github
* It uses [misaka](http://misaka.61924.nl/) which is a python-binding of [sundown](https://github.com/tanoku/sundown), the markdown engine that github uses in itself

# Example

## unicode.lower transforms string into lowercase

```python
assert u"Gabriel Falcão".lower() == "gabriel falcão"
```

## python can add numbers

```python
assert (2 + 2) == 4, 'oops baby'
```

# Start using steady mark now!

This is the code for the example above, copy and paste in you python
project right now and start keeping your documentation up-to-date with
the code.

    # My project name
    `version 0.1`

    ## unicode.lower transforms string into lowercase

    ```python
    assert "LOWERCaSe".lower() == "lowercase"
    ```

    ## python can add numbers

    ```python
    assert (2 + 2) == 5, 'oops baby'
    ```

Just run with:

```bash
$ steadymark README.md
```

# Steadymark is on version 0.1.4

```python
from steadymark import version
assert version == '0.1.4'
```

# Steadymark strips headers

```python
from sure import that
from steadymark import Runner

assert that(Runner(text='## test\n```python\nassert True\n```').run().tests).equals([{u'code': u'assert True', u'title': u'test'}])
```
