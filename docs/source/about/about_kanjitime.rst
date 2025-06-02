History of  Kanji Time
======================

It's 漢字タイム!

Kanji Time started life as a small project created over the 2024 holiday break by Andrew Milton to help with his study of Japanese language and kanji.

It is in part inspired by the fabulous website `jisho.org <https://jisho.org/>`_, where one is able to take a deep dive into the individual kanji in a compound and explore it detail.
Jisho made it easy for the author to identify patterns, pseudo-patterns, and anti-patterns in kanji across Japanese words.

Original Goals
--------------

The project goal was to couple an offline information sheet about a kanji to a practice worksheets for stroking it.
The overarching idea is cement a kanji in memory by its strokes and by it different interpretations in the context of its various word compounds.

I looked to the same trusted data sources a `jisho.org` to generate two items:

1. printable exercise sheets containing stroke diagrams and ruled areas to practice a kanji character, and,
2. consistently formatted kanji summaries that contains readings, radical information, and definitions.

The author could acheve most of this from a Jupyter Notebook and supporting IPython services - but it quickly became apparent that to get polished results, we'd need to integrate layout and PDF output into the code.

We'd need to up our game from a notebook to a Python console application.

Kanji Time is born!
-------------------

The new application is "Kanji Time" and the result is in front of you.

The Kanji time app only has two PDF outputs at present at this time to prove out the concept.
These are just the beginning!
Kanji Time incorporates a flexible drop-in report architecture and simple reusable layout rules that easily allow for future expansion to new exercise sheets such as:

    - exploring small groups of compound kanji words connected through a common theme (such as a common stroke group, prefix/suffix, readings, or sounds),
    - reviewing different conjugations and declensions, or,
    - practicing hiragana or katakana penmanship.

The possibilities are endless - extensibility and growth are baked in as core design principals.

New Goals Emerge
----------------

As I was developing Kanji Time I was looking ahead to the upcoming session of `Code In Place (CiP) <https://codeinplace.stanford.edu>`_.  I realized that Kanji Time could make an interesting example the my CiP section students of what "real-life" Python programming looks like.

To that end I set some smaller goals:

   * The resulting program must solve a well-defined and useful problem.
   * The code shouldn't be obscure - keep to well-known and well-understood Python introductory to intermediate features and libraries.  This means no `async` - at least on this branch.
   * Keep the project to about 4000 lines of code - big enough to be meaty yet small enough to hold in your head comfortably.
   * Demonstrate the trade-offs between design purity and coding expediency.
   * Demonstrate the use of "design patterns" in the wild in a real project.
   * Have several clear paths for fleshing out new features and capabilities.
   * Keep documentation and testing as first-class citizens in the project.
   * Exploit simuluated intelligence and simulated competency tools for software development, such as OpenAI's o1 and 4o LLM instances.

Technology
----------

Kanji Time is built on top of the Python 3.11 ecosystem.  Along with standard library packages, it uses:

    #. Sphinx 8.2.3 for generating documentation,
    #. sphinxcontrib-mermaid 1.0.0 for generating diagrams,
    #. pytest 8.3.5 for automatic testing,
    #. pylint 3.3.7 for enforcing code hygiene,
    #. reportlab 4.2.5 for generating PDF output, and,
    #. svgwrite 1.4.3 for generating scalable graphics.

Kanji Time imports data from

    #. kanji_dict and kanji_dic2, both from the ELECTRONIC DICTIONARY RESEARCH AND DEVELOPMENT GROUP (EDRDG), for Kanji information, and,
    #. Kanji SVG from Ulrich Apel

All of these imported data are used unaltered from their source.

.. _licensing:

Licenses
--------

Kanji Time is a mixed-license project.
The code is released under the GNU AGPL v3.0, while the accompanying documentation is licensed under CC BY-SA 4.0.
It redistributes third-party data sets under their original licenses: KanjiDic2 and KanjiVG under CC BY-SA 4.0, and Unicode CJKRadicals.txt under the Unicode License Version 3.0.

All redistributed data is included in its original, unmodified form.

For full details, see:

.. toctree::
    :maxdepth: 1

    license
    notice
    third_party_licenses

