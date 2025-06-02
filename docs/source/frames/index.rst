Content Frames
==============

This section documents all rendering frame components that support the layout engine in Kanji Time.

Content frames implement the `RenderingFrame` protocol, enabling them to measure, lay out, and draw themselves independently.
Frames may be atomic (self-contained) or composite (containing other frames), and may stretch or paginate depending on context.

The overall layout model is compositional.
Container frames use layout strategies to position their children.
The `Page` class extends this pattern to define page-level constraints and orchestrate multi-page output.

----

Atomic Frames and Containers
----------------------------

These are the core architectural building blocks of the layout system.

.. toctree::
   :maxdepth: 2

   simple_element
   container
   strategy
   stack_layout
   page

----

Specialized Atomic Content Frames
---------------------------------

These provide specific rendering logic for formatted text, vector diagrams, horizontal rules, and spacing blocks.

.. toctree::
   :maxdepth: 2

   formatted_text
   drawing
   page_rule
   empty_space
