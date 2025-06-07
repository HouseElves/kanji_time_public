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
        look: handDrawn
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

"""
import pathlib

EXTERNAL_DATA_ROOT : pathlib.Path = pathlib.Path(__file__).parent
