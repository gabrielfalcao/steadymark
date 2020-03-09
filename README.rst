Steady Mark
===========

.. image:: https://img.shields.io/pypi/dm/steadymark
   :target: https://pypi.org/project/steadymark

.. image:: https://img.shields.io/codecov/c/github/gabrielfalcao/steadymark
   :target: https://codecov.io/gh/gabrielfalcao/steadymark

.. image:: https://img.shields.io/github/workflow/status/gabrielfalcao/steadymark/python-3.6?label=python%203.6
   :target: https://github.com/gabrielfalcao/steadymark/actions

.. image:: https://img.shields.io/github/workflow/status/gabrielfalcao/steadymark/python-3.7?label=python%203.7
   :target: https://github.com/gabrielfalcao/steadymark/actions

.. image:: https://img.shields.io/github/license/gabrielfalcao/steadymark?label=Github%20License
   :target: https://github.com/gabrielfalcao/steadymark/blob/master/LICENSE

.. image:: https://img.shields.io/pypi/v/steadymark
   :target: https://pypi.org/project/steadymark

.. image:: https://img.shields.io/pypi/l/steadymark?label=PyPi%20License
   :target: https://pypi.org/project/steadymark

.. image:: https://img.shields.io/pypi/format/steadymark
   :target: https://pypi.org/project/steadymark

.. image:: https://img.shields.io/pypi/status/steadymark
   :target: https://pypi.org/project/steadymark

.. image:: https://img.shields.io/pypi/pyversions/steadymark
   :target: https://pypi.org/project/steadymark

.. image:: https://img.shields.io/pypi/implementation/steadymark
   :target: https://pypi.org/project/steadymark

.. image:: https://img.shields.io/snyk/vulnerabilities/github/gabrielfalcao/steadymark
   :target: https://github.com/gabrielfalcao/steadymark/network/alerts

.. image:: https://img.shields.io/github/v/tag/gabrielfalcao/steadymark
   :target: https://github.com/gabrielfalcao/steadymark/releases


Turning your github readme files into python test suites since 2012
===================================================================

Steady Mark was created for python developers that love Github and
markdown.

How it works:
-------------

Write your documentation using `github-flavored
markdown <http://github.github.com/github-flavored-markdown/>`__,
surround your snippets with python code blocks and steadymark will
automatically find and run them, if there is a header preceeding your
python snippet it will be used as title for your test.

Advantages:
===========

-  Add test coverage to your app/library while documenting it
-  Never have old malfunctional examples on your project’s main page in
   github
-  It uses `misaka <http://misaka.61924.nl/>`__ which is a
   python-binding of `sundown <https://github.com/tanoku/sundown>`__,
   the markdown engine that github uses in itself

Example
=======

unicode.lower transforms string into lowercase
----------------------------------------------

.. code:: python

   from sure import expect
   assert expect(u"Gabriel Falcao".lower()).equals(u"gabriel falcao")

python can add numbers
----------------------

.. code:: python

   assert (2 + 2) == 4, 'oops baby'

Start using steady mark now!
============================

This is the code for the example above, copy and paste in you python
project right now and start keeping your documentation up-to-date with
the code.

::

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

.. code:: bash

   $ steadymark README.md

loading a python file before running tests
------------------------------------------

you can tell steadymark to load a “boot” file before running the tests,
it’s very useful for hooking up `sure <http://falcao.it/sure>`__ or
`HTTPretty <http://falcao.it/HTTPretty>`__

Steadymark is on version 0.8.0
==============================

.. code:: python

   >>> from sure import expect
   >>> from steadymark import version
   >>> assert expect(version).should.equal("0.8.0")
