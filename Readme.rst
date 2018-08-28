Python XLIFF Converter
######################

This package provides a set of utilities for converting rich-text markup files
to `OASIS XLIFF`_ translatable format. Currently only HTML <=> XLIFF 1.2 conversion
is supported.

Installation
============

Python XLIFF Converter can be installed using pip::

  pip install py-xliff-converter

Usage
=====

HTML => XLIFF
-------------

Command line::

  html2xliff <myfile>.html

This command will create ``<myfile>.xlf`` file that can be translated using most
common online and offline CAT tools: Trados, memoQ, Transifex etc.

API:

.. code-block:: python

  from xliff_converter.html_parser import convert_html
  ...
  with open(html_filename, 'r', encoding='utf-8') as fo:
      html = fo.read()
  xliff = convert_html(html, html_filename)
  ...

The ``convert_html(...)`` function returns translatable XLIFF document as ``bytes``
string encoded in UTF-8.

XLIFF => HTML
-------------

Command line::

  xliff2html <myfile>.xlf

This command will create ``<myfile>_<lang>.html`` file containing translated
content of the source HTML file. ``<lang>`` is the language code of a target
language.

API:

.. code-block:: python

  from xliff_converter.html_rebuilder import rebuild_html
  ...
  with open(xliff_filename, 'r', encoding='utf-8') as fo:
      xliff = fo.read()
  filename, html = rebuild_html(xliff)

The ``rebuild_html(...)`` function returns a tuple (named tuple) containing
the name of a translated HTML file and its contents as ``str``.

Notes
=====

- Currently Python XLIFF Converter supports only English as a source language.
- Translatable text is segmented by sentences using `NLTK`_ sentence tokenizer.
- The HTML converter accepts partial HTML markup, e.g. ``<body>`` tag
  contents and even plain text.
- ``<br>`` tags are treated as translation segment delimiters.
- ``<pre><code>...</code></pre>`` blocks are ignored.

To do
=====

- More file formats.
- XLIFF 2.0 support.

.. _OASIS XLIFF: https://en.wikipedia.org/wiki/XLIFF
.. _NLTK: https://www.nltk.org
