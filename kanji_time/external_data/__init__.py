# __init__.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Model data imported from outside of Kanji Time.

Internal Dependencies
---------------------

The Python code modules in :mod:`external_data` depend on each other per the below diagram.

.. mermaid::
    :caption: external_data - Internal Module Dependencies

    ---
    config:
        layout: elk
        :zoom:
    ---
    flowchart TD

    kanji_dic2[kanji_dic2.py]
    radicals[radicals.py]
    settings[settings.py]
    kanji_dict[kanji_dict.py]
    kanji_svg[kanji_svg.py]

    radicals --> kanji_dic2
    kanji_dic2 --> settings
    kanji_dict --> settings
    kanji_svg --> settings


External Dependencies
---------------------

The Python code modules in :mod:`external_data` depend on modules external to the package and on libraries per the below diagram.

.. mermaid::
    :caption: external_data - External Module Dependencies
    :zoom:

    ---
    config:
        layout: elk
    ---
    flowchart LR

    kanji_svg[kanji_svg.py];
    radicals[radicals.py];
    subgraph root
        svg_transform[svg_transform.py];
    end
    subgraph Python Libraries
        svgwrite[[svgwrite]];
        IPython[[ipython]];
    end
    subgraph utilities
        general[general.py]
        check_attrs[check_attrs.py]
    end
    subgraph vl[visual.layout]
        distance[distance.py];
        region[region.py];
    end

    vl_comment@{shape: brace, label: "distance & region to be moved to houseelves.geometry"}
    distance ~~~ vl_comment
    region ~~~ vl_comment

    st_comment@{shape: brace, label: "svg_transform belongs in the adapter layer"}
    svg_transform ~~~ st_comment

    kanji_svg --> svg_transform
    kanji_svg --> svgwrite
    kanji_svg --> IPython
    kanji_svg --> general
    kanji_svg --> distance
    kanji_svg --> region

    radicals --> check_attrs

Package Contents
----------------

.. toctree::
   :maxdepth: 1
   :caption: External Data Package

   kanji_dic2.py   <kanji_dic2.py>
   kanji_dict.py   <kanji_dict.py>
   kanji_svg.py    <kanji_svg.py>
   radicals.py     <radicals.py>
   settings.py     <settings.py>

----

.. only:: dev_notes

    .. seealso::

        - :ref:`embedded_content` for credits and licensing for 3rd party data used in Kanji Time.
        - :ref:`data plans <data_plans>` for notes about converting XML data to an SQL RDBMS platform.
        - :ref:`radicals <radicals>` for notes about extending the range of radical and kana data available in Kanji Time
        - :ref:`external_data_notes` for raw developer source code notes

"""
import pathlib

EXTERNAL_DATA_ROOT : pathlib.Path = pathlib.Path(__file__).parent
