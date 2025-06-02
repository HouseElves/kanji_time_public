============================
List of Diagrams and Figures
============================

.. contents::
   :local:
   :depth: 1


Class Relationships
-------------------

Class relationship diagrams linked below.

.. table::

    ============================== ============================
    class                          link
    ============================== ============================
    :mod:`kanji_time`              :ref:`comp_CLI_Components`
    :class:`Container`             :ref:`cd_container`
    :class:`Page`                  :ref:`cd_page`
                                   :ref:`cd_pagedetail`
    :class:`PageSettings`          :ref:`cd_pagesettings`
    :class:`kanji_summary.Report`  :ref:`cd_infosheet`
                                   :ref:`cd_infosheet_detail`
    :class:`KanjiSummary`          :ref:`cd_infosheet_kanji`
    :class:`RadicalSummary`        :ref:`cd_infosheet_radical`
    :class:`KanjiReportData`       :ref:`cd_infosheet_data`
    :class:`SummaryBanner`         :ref:`cd_infosheet_banner1`
    :class:`SummaryBannerPage2On`  :ref:`cd_infosheet_banner2`
    :class:`practice_sheet.Report` :ref:`cd_practicesheet`
                                   :ref:`cd_practicesheet_detail`
    :class:`PracticeSheetData`     :ref:`cd_practicesheet_data`
    :class:`KanjiSVG`              :ref:`cd_kanjisvg`
    :class:`Radical`               :ref:`cd_radicaldata`
    :class:`PageController`        :ref:`cd_pagecontroller`
    :class:`ReportLabDrawing`      :ref:`cd_drawing`
    :class:`EmptySpace`            :ref:`cd_emptyspace`
    :class:`FormattedText`         :ref:`cd_formatted_text`
    :class:`HorizontalRule`        :ref:`cd_rule`
    :class:`SimpleElement`         :ref:`cd_simple_element`
    Geometry Model                 :ref:`cd_geometry`
    :class:`Distance`              :ref:`cd_geometry_distance`
    :class:`StackLayoutStrategy`   :ref:`cd_stack_layout`
                                   :ref:`cd_stack_layout_detail`
    ============================== ============================

Kanji Time Processes
--------------------

.. table::

    ============================== ==================================
    Python item                    link
    ============================== ==================================
    :class:`Page`                  :ref:`sd_single_page`
    :class:`kanji_summary.Report`  :ref:`sd_infosheet_dynamic_layout`
                                   :ref:`fc_infosheet_generate`
    :py:func:`Container.measure`   :ref:`sd_container_measure`
    :py:func:`FormattedText.draw`  :ref:`sd_formatted_text_draw`
                                   :ref:`st_formatted_text_draw`
    ============================== ==================================


Geometry and Positioning
------------------------

- **PageSettings Printable Region**
  Detailed margin and printable area diagram (ASCII art).

- **Region Coordinate System** *(TODO)*
  Coordinate system with examples of region shifting.

Layout and Rendering
--------------------

- **Pagination Sequence Diagram**
  Mermaid diagram showing the interaction loop (Controller → PageFactory → Page → ContentFrame).

- **ContentFrame Size Negotiation Flow** *(TODO)*
  Flowchart of interactions between `requested_size`, `measure()`, and `layout()`.

- **StackLayoutStrategy Flowchart** *(TODO)*
  Diagram showing measurement and layout flow within StackLayoutStrategy.

- **Rendering Frame Hierarchy** *(TODO)*
  UML class diagram showing RenderingFrame inheritance and composition structure.

Positional and Anchoring
------------------------

- **Pos and AnchorPoint Relationships** *(TODO)*
  Diagram illustrating positional relationships and anchoring logic.
