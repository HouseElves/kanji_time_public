# __init__.py
# Copyright (C) 2024, 2025 Andrew Milton
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Implement the Kanji Stroke Diagram & Practice Sheet

Internal Dependencies
---------------------

.. mermaid::
    :caption: reports.practice_sheet - Internal Module Dependencies

    ---
    config:
        layout: elk
    ---
    flowchart TD

    report[report.py]
    document[document.py]

    report --> document


External Dependencies
---------------------

.. mermaid::
    :caption: practice_sheet - External Module Dependencies

    ---
    config:
        layout: elk
    ---
        flowchart LR

        subgraph ps_document
            direction TB
            document[document.py];
            d_comment@{shape: braces, label: "imports distance for **Distance** unit conversions in logging and region to use an **Extent** for the kanji & grid drawing sizes."}
        end
        ps_report[report.py];

        subgraph visual
            subgraph vl[visual.layout];
                region[region.py];
                anchor_point[anchor_point.py];
                stack_layout[stack_layout.py];
                distance[distance.py];
                vl_comment@{shape: braces, label: "distance & region to be moved to a geometry package"}
            end
            subgraph vf[visual.frame]
                drawing[drawing.py];
                formatted_text[formatted_text.py];
            end
        end
        distance ~~~ vl_comment
        region ~~~ vl_comment



        subgraph reports
            controller[controller.py];
            settings[settings.py];
        end
        subgraph adapter
            svg[svg.py];
            svg_comment@{shape: braces, label: "Provides an SVG <--> ReportLab drawing conversion."}
        end
        svg ~~~ svg_comment

        subgraph lib[Python Libraries]
            rl_lib[[reportlab.lib]];
            rl_pdf[[reportlab.pdfbase]];
            rl_p[[reportlab.platypus]];
        end
        subgraph utilities
            general[general.py];
            xml[xml.py];
        end
        subgraph external_data
            kanji_svg[kanji_svg.py];
            ksvg_comment@{shape: braces, label: "This should be factored into drawing services and data services."}
        end
        kanji_svg ~~~ ksvg_comment

        ps_document --> distance
        ps_document --> kanji_svg
        ps_document --> region
        ps_document --> svg

        ps_report --> anchor_point
        ps_report --> controller
        ps_report --> stack_layout
        ps_report --> formatted_text
        ps_report --> drawing
        ps_report --> general
        ps_report --> rl_lib
        ps_report --> rl_p
        ps_report --> rl_pdf
        ps_report --> rl_pdf
        ps_report --> settings
        ps_report --> xml

"""
