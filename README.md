# Steady Mark
[![Build Status](https://secure.travis-ci.org/gabrielfalcao/steadymark.png)](http://travis-ci.org/gabrielfalcao/steadymark)

# Turning your github readme files into python test suites since 2012

Steady Mark was created for python developers that love Github and
markdown.

## How it works:

Write your documentation using github-flavored markdown, surround your
snippets with python code blocks and steadymark will automatically
find and run them, if there is a header preceeding your python snippet
it will be used as title for your test.

# Example

Given the following `README.md`:

    # My project name
    `version 0.1`

    ## usage

    ```python
    from mylibrary import whatever

    whatever.awesome()
    ```

Just run with:

```console
$ steadymark README.md
```
