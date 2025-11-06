===========
Source Code
===========

Jump to the code: :ref:`sources_root`

Kanji Time Package Structure
----------------------------

Kanji time breaks down naturally into five packages:

    **utilities**
        General purpose helpers, such as a :deco:`classproperty` decorator or a list flattener :func:`flatten`.

    **adapter**
        Translation layers to shoehorn one technology into another, such as adapting `svgwrite` to work with `ReportLab`.

    **external_data**
        Interface layers into data consumed by the `reports` package, such as kanji stroke diagrams or kanji interpretations.

    **visual**
        Data presentation and layout tools for visualizing data and another page content in the `reports` package.

    **reports**
        Coordinating controllers for combining data and presentation into well defined reports such as the Kanji Summary or Practice Sheet.

The below diagram visualizes this structure.

.. mermaid::
    :name: components
    :caption: Kanji Time internal package structure.

    ---
    config:
        layout: elk
    ---
    flowchart TB
    classDef hidden display: none;

    subgraph vis["visual package"]
        direction TB
        v["visual"]
        p["visual.protocol"]
        l["visual.layout"]
        f["visual.frame"]
        yyy:::hidden ~~~ p
        v --> p & l & f
    end
    subgraph rep["reports package"]
        direction TB
        reports
        ks["reports.kanji_summary"]
        ps["reports.practice_sheet"]
        xxx:::hidden ~~~ ks
        reports --> ps & ks
    end
    subgraph data["external data package"]
        direction TB
        d[external_data]
        kd[("KanjiDict")]
        kd2[("KanjiDic2")]
        ksvg[("Kanji SVG")]
        rad[("Unicode CJK<br>Radicals")]
        zzz:::hidden ~~~ ksvg
        d --> kd & kd2 & ksvg & rad
    end

    subgraph ad["adapter package"]
        adapter
    end
    subgraph util["utilities package"]
        utilities
    end

    subgraph root["project root"]
        direction TB
        cli("Kanji Time<br>Command Line")
    end
    x:::hidden ~~~ data
    root --> ad & util & data & vis & rep

This breakdown is mirrored in the directory structure in the project:

.. literalinclude:: dirsonly

.. _sources_root:

Project Root
------------

The project root contains the main entry point for Kanji time and the internal package directories.

.. toctree::
   :maxdepth: 2

   __init__.py
   __main__.py
   settings.py
   kanji_time_cli.py
   svg_transform.py


Package Source Code
-------------------

.. toctree::
   :maxdepth: 1

   adapter/index
   external_data/index
   visual/index
   reports/index
   utilities/index


Raw Development Notes
---------------------

Raw code development notes extracted from the source files.

   :ref:`dev_notes`

