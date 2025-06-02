======================================
HTML-like Markup: FormattedText Frames
======================================

Python code file: visual/frame/formatted_text.py

The `FormattedText` frame renders rich text paragraphs using ReportLab's HTML-like markup. It wraps, flows, and paginates content dynamically.

It differs from most atomic frames in that:

- Its height depends on the available width (due to wrapping).
- It tracks and optionally consumes content across pages.
- It interacts with ReportLab `Flowable` and `Paragraph` instances.

Use `FormattedText` when you need to handle scrollable or styled content blocks with layout-sensitive rendering.

----

.. automodule:: kanji_time.visual.frame.formatted_text
     :members:
