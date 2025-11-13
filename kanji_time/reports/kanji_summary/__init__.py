# __init__.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Implement the dictionary lookup report for a kanji glyph.


Internal Dependencies
---------------------

.. mermaid::
    :caption: reports.kanji_summary - Internal Module Dependencies

    ---
    config:
        layout: elk
    ---
    flowchart TD

    report[report.py]
    document[document.py]
    banner[banner.py]
    kanji_summary[kanji_summary.py]
    radical_summary[radical_summary.py]

    report --> banner
    banner --> kanji_summary
    banner --> radical_summary
    radical_summary --> document


External Dependencies
---------------------

.. mermaid::
    :caption: reports.kanji_summary - External Module Dependencies

    ---
    config:
        layout: elk
    ---
    flowchart LR

    subgraph ks_document
        direction TB
        document[document.py];
        d_comment@{shape: braces, label: "imports region to use an **Extent** for the kanji drawing size."}

    end
    ks_report[report.py];
    banner[banner.py];
    kanji_summary[kanji_summary.py];
    radical_summary[radical_summary.py];

    subgraph visual
        subgraph vl[visual.layout];
            region[region.py];
            anchor_point[anchor_point.py];
            stack_layout[stack_layout.py];
        end
        subgraph vf[visual.frame]
            container[container.py];
            drawing[drawing.py];
            formatted_text[formatted_text.py];
            page_rule[page_rule.py];
            empty_space[empty_space.py];
            simple_element[simple_element.py];
        end
    end


    subgraph reports
        controller[controller.py];
        settings[settings.py];
    end
    subgraph adapter
        svg[svg.py];
    end

    subgraph lib[Python Libraries]
        rl_lib[[reportlab.lib]];
        rl_pdf[[reportlab.pdfbase]];
        rl_p[[reportlab.platypus]];
        rl_c[[reportlab.rl_config]];
    end
    subgraph utilities
        general[general.py];
        xml[xml.py];
    end
    subgraph external_data
        kanji_dic2[kanji_dic2.py];
        kanji_dict[kanji_dict.py];
        kanji_svg[kanji_svg.py];
        radicals[radicals.py];
    end


    ks_report --> anchor_point
    ks_report --> controller
    ks_report --> stack_layout
    ks_report --> formatted_text
    ks_report --> page_rule
    ks_report --> settings
    ks_report --> general
    ks_report --> rl_c
    ks_report --> rl_lib
    ks_report --> rl_pdf


    ks_document --> general
    ks_document --> kanji_dic2
    ks_document --> kanji_dict
    ks_document --> kanji_svg
    ks_document --> radicals
    ks_document --> region
    ks_document --> svg
    ks_document --> xml
    ks_document --> rl_c
    ks_document --> rl_lib
    ks_document --> rl_p


    banner --> container
    banner --> drawing
    banner --> formatted_text
    banner --> stack_layout


    kanji_summary --> simple_element
    kanji_summary --> empty_space
    kanji_summary --> formatted_text
    kanji_summary --> rl_p

    radical_summary --> anchor_point
    radical_summary --> simple_element
    radical_summary --> drawing
    radical_summary --> formatted_text

Package  Contents
-----------------

.. toctree::
   :maxdepth: 1
   :caption: Kanji Summary

   report.py <report.py>
   document.py <document.py>
   banner.py <banner.py>
   kanji_summary.py <kanji_summary.py>
   radical_summary.py <radical_summary.py>


"""
