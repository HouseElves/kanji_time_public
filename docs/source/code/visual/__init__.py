"""
Implement tools that present data: the "visual" elements.

Structure
---------

The `visual` package splits along three lines:

    protocol
        the polymorphic Python protocols for layout strategies & rendering frames

    frame
        implementations of :class:`RenderingFrame` specialized to present different types of content, such as drawings or formatted text.

    layout
        particulars for arranging frames on a page, including layout strategies and basic geometry

The below diagram visualizes this structure.

.. mermaid::
    :caption: visual package - subpackage structure

    ---
    config:
        layout: elk
    ---
    flowchart TD
    classDef hidden display: none;

    visual[[visual]]
    protocol[[protocol]]
    frame[[frame]]
    layout[[layout]]

    frame_c@{shape: braces, label: "holders for page content"}
    layout_c@{shape: braces, label: "arrangers of page content frames"}
    protocol_c@{shape: braces, label: "common interfaces for all visual elements"}

    dummy:::hidden ~~~ layout
    visual --> protocol
    visual --> frame
    visual --> layout
    protocol ~~~ protocol_c
    frame ~~~ frame_c
    layout ~~~ layout_c


Dependencies
------------

The `visual` package is mostly self-contained.
It relies on some technology libraries (such as for SVG services and PDF rendering) that will eventually be factored out to a generic
technology service, that that's low on the priority list until there's a compelling code reason to do it sooner.

There's some refactoring to done to isolate the geometry from the layout and to make a package for modeling physical-world objects (such as
paper in various sizes etc.)

.. mermaid::
    :caption: visual package - all internal/external dependencies with transitive suppression

    ---
    config:
        layout: elk
    ---
        flowchart TD

        subgraph lib[Python Libraries]
            rl_lib[[reportlab.lib]];
            rl_pdfg[[reportlab.pdfgen]];
            rl_p[[reportlab.platypus]];
            svgwrite[[svgwrite]];
            sw_data[[svgwrite.data]];
            svglib[[svglib]];
        end

        subgraph utilities
            general[general.py];
            class_property[class_property.py];
        end
        subgraph adapter
            svg[svg.py];
        end
        subgraph visual
            subgraph vl[visual.layout];
                distance[distance.py];
                region[region.py];
                anchor_point[anchor_point.py];
                paper_names[paper_names.py];
                pn_comment@{shape: braces, label: "'paper_names' should go in a 'visual.physical' package."}
                paper_names ~~~ pn_comment
                region --> anchor_point
                region --> distance
            end
            subgraph protocol[visual.protocol]
                content[content.py];
                layout_strategy[layout_strategy.py];
            end
            subgraph vf[visual.frame]
                container[container.py];
                page[page.py];
                simple_element[simple_element.py];
                formatted_text[formatted_text.py];
                drawing[drawing.py];
                page_rule[page_rule.py];
                empty_space[empty_space.py];

                drawing ---> simple_element
                empty_space ---> simple_element
                formatted_text ---> simple_element
                page_rule ---> simple_element

                simple_element --> content

                page --> container
                content --> region
            end
            container --> content
            container --> layout_strategy
            layout_strategy --> region

        end
        drawing --> svg
        content --> rl_pdfg
        formatted_text --> rl_p
        page --> paper_names
        region --> class_property
        distance --> class_property
        container --> general
        container --> rl_lib

        svg --> svglib
        svg --> svgwrite
        svg --> sw_data
        svg --> sw_data

----

"""
