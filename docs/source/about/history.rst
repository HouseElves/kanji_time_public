History of Kanji Time
=====================

It's 漢字タイム!

Kanji Time started life as a small project created over the 2024 holiday break by Andrew Milton to help with his study of Japanese language and kanji.

It is in part inspired by the fabulous website `jisho.org <https://jisho.org/>`_, where one is able to take a deep dive into the individual kanji in a compound and explore it in detail.
Jisho made it easy for the author to identify patterns, pseudo-patterns, and anti-patterns in kanji across Japanese words.

Original Goals
--------------

The project goal was to couple an offline information sheet about a kanji to a practice worksheet for stroking it.
The overarching idea is to cement a kanji in memory by its strokes and by its different interpretations in the context of its various word compounds.

I looked to the same trusted data sources as `jisho.org` to generate two items:

1. printable exercise sheets containing stroke diagrams and ruled areas to practice a kanji character, and,
2. consistently formatted kanji summaries that contain readings, radical information, and definitions.

The author could achieve most of this from a Jupyter Notebook and supporting IPython services - but it quickly became apparent that to get polished results, we'd need to integrate layout and PDF output into the code.

We'd need to up our game from a notebook to a Python console application.

Kanji Time is born!
-------------------

The new application is "Kanji Time" and the result is in front of you.

The Kanji Time app only has two PDF outputs at this time to prove out the concept.
These are just the beginning!
Kanji Time incorporates a flexible drop-in report architecture and simple reusable layout rules that easily allow for future expansion to new exercise sheets such as:

    - exploring small groups of compound kanji words connected through a common theme (such as a common stroke group, prefix/suffix, readings, or sounds),
    - reviewing different conjugations and declensions, or,
    - practicing hiragana or katakana penmanship.

The possibilities are endless - extensibility and growth are baked in as core design principles.

New Goals Emerge
----------------

As I was developing Kanji Time I was looking ahead to the upcoming session of `Code In Place (CiP) <https://codeinplace.stanford.edu>`_.  I realized that Kanji Time could make an interesting example to my CiP section students of what "real-life" Python programming looks like.

To that end I set some smaller goals:

   * The resulting program must solve a well-defined and useful problem.
   * The code shouldn't be obscure - keep to well-known and well-understood Python introductory to intermediate features and libraries.  This means no `async` - at least on this branch.
   * Keep the project to about 4000 lines of code - big enough to be meaty yet small enough to hold in your head comfortably.
   * Demonstrate the trade-offs between design purity and coding expediency.
   * Demonstrate the use of "design patterns" in the wild in a real project.
   * Have several clear paths for fleshing out new features and capabilities.
   * Keep documentation and testing as first-class citizens in the project.
   * Exploit simulated intelligence and simulated competency tools for software development, such as OpenAI's o1 and 4o LLM instances.
