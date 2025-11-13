About Kanji Time
================

Learning kanji requires both analytical understanding and physical practice. 
Kanji Time bridges this gap by generating customized study materials that couple stroke practice with linguistic context.

Built on Python 3.11, Kanji Time transforms data from trusted sources (KanjiDic2, KanjiVG) into professional PDF worksheets and reference sheets tailored to your study needs.

Core Capabilities
-----------------

**Practice Sheets**
    Stroke-order diagrams with ruled grids for penmanship practice

**Summary Sheets**
    Readings, radicals, and compound word examples in consistent layouts

**Extensible Architecture**
    Drop-in report modules, reusable layout primitives, and pluggable strategies for future expansion

----

For the story of how Kanji Time evolved from a holiday project into an extensible report generation engine, see :doc:`history`.

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

Kanji Time uses these data in their original unaltered form.

Licensing details available in :doc:`../licensing`