.. _third-party-licenses:

Third-Party Licenses
====================

Development of Kanji Time requires several third-party Python packages disclosed below. Each dependency is either bundled during development or used at runtime under the terms of its original license.

pytest 8.3.5
------------

**Description**: Testing framework for Python
**License**: MIT License
**URL**: https://github.com/pytest-dev/pytest

You may use, modify, and distribute `pytest` under the terms of the MIT License. This software is used for development and is not distributed as part of the final application.

pylint 3.3.7
------------

**Description**: Code analysis and linting tool
**License**: GNU General Public License v2.0 or later (GPL-2.0-or-later)
**URL**: https://github.com/pylint-dev/pylint

`pylint` is used only during development to enforce code quality. It is not bundled or redistributed. The copyleft terms of the GPL do not apply to this project unless `pylint` itself is distributed.

reportlab 4.2.5
---------------

**Description**: PDF generation library for Python
**License**: BSD 3-Clause License
**URL**: https://www.reportlab.com/devops/open-source/

`reportlab` is used at runtime to generate PDFs. If you redistribute a modified version of this library, the BSD 3-Clause License requires you to retain the original copyright. Kanji Time does not modify any portion of reportlab.

svgwrite 1.4.3
--------------

**Description**: A Python library to write SVG files
**License**: MIT License
**URL**: https://github.com/mozman/svgwrite

`svgwrite` is a permissively licensed library used to create scalable vector graphics. It places no restrictions on redistribution or commercial use.

See Also
--------

For attribution and licensing of redistributed data sets (e.g., KanjiDic2, KanjiVG, Unicode CJKRadicals), refer to:

* :doc:`notice`
* :doc:`license`
