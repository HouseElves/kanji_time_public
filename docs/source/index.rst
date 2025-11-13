:orphan:

.. include:: /common

.. only:: nonlinear_flow

    .. image:: _static/kanji_time_title_byline.svg
       :alt: Kanji Time!
       :scale: 50%
       :align: center
       :width: 100pc
       :height: 25pc

    .. container:: center

        **Kanji Time is an extensible tool that instantly generates custom, printable kanji study sheets and dictionary summaries.**

        With future-forward design and plug-in reporting, Kanji Time is also a powerful launching platform for plug-in database-to-PDF report execution.

    .. admonition:: Command Line Quick Start

       python -m kanji_time 生 --report=kanji_summary

    .. grid:: 1 1 2 2
       :gutter: 3

       .. grid-item-card:: Get Started with Kanji Time

            * :doc:`installation` - Set up Kanji Time
            * :doc:`usage` - Generate your first worksheet
            * :doc:`samples`- See Kanji Time can do

       .. grid-item-card:: Architecture

            * :doc:`design/review` - The Kanji Time philosophy
            * .. dropdown:: Kanji Time Internals
                 :animate: fade-in-slide-down
                 :class-title: reference
                 :chevron: down-up

                    * :doc:`Command Line & Dispatch <design/cli_entry>`
                    * :doc:`Adding On Reports <design/report_addon>`
                    * :doc:`Laying Out Page Components <design/page_layout>`
                    * :doc:`Defined Content Frames <design/packaged_frames>`
                    * :doc:`Open Source Data <design/external>`
                    * :doc:`Immutable Geometry Primitives <design/geometry>`

            * :doc:`road_ahead_redux`- Upcoming work

       .. grid-item-card:: Licenses & About

            * :doc:`licensing` - Kanji Time & 3rd Party
            * :doc:`about/about_kanjitime` - Elevator Pitch
            * :doc:`about/about_docs` - Tools

       .. grid-item-card:: Developer's Reference

            * .. dropdown:: Components Overview
                 :animate: fade-in-slide-down
                 :class-title: reference
                 :chevron: down-up

                    * :doc:`data/index`
                    * :doc:`frames/index`
                    * :doc:`geometry/index`
                    * :doc:`reports/index`

            * :doc:`code_stubs/development` - Implementation details

    ----

    .. toctree::
       :hidden:
       :caption: Welcome

       overview

    .. toctree::
       :hidden:
       :caption: Getting Started

       installation
       usage
       samples

    .. toctree::
       :hidden:
       :caption: Architecture & Internals

       design/review
       internals
       road_ahead_redux

    .. toctree::
       :hidden:
       :caption: Developer Guide & Reference

       dev_guide/index
       code_stubs/development

    .. toctree::
       :hidden:
       :caption: Licenses and About

       licensing
       about/about_kanjitime
       about/about_docs

    **Kanji Time makes PDFs for you containing:**

    .. grid:: 1 1 2 3
       :gutter: 3

       .. grid-item-card:: a ruled kanji practice grid with a stroke diagram
          :text-align: center

          .. image:: _static/grid_image.png
             :alt: Sample ruled kanji penmanship practice grid
             :width: 100%

       .. grid-item-card:: dictionary information for a Kanji
          :text-align: center

          .. image:: _static/summary_image.png
             :alt: Extract from a sample Kanji Summary
             :width: 100%

       .. grid-item-card:: a step-by-step kanji stroke sequence
          :text-align: center

          .. image:: _static/strokes_image.png
             :alt: Sample kanji stroke diagram
             :width: 100%

See :ref:`samples` to look at full sized Kanji Summary and Practice Sheet PDFs with these features!




