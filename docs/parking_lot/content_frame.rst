==================================================
Position Renderable Content: ContentFrame Protocol
==================================================

Python entry point: `visual/protocol/content.py``

Kanji Time separates layout logic from rendering concerns through a unified interface called the ``ContentFrame`` protocol.

All elements that appear in a report — whether atomic (like text boxes or glyphs) or composite (like containers or pages) — conform to this protocol.

This interface standardizes three responsibilities across all visual elements:

- **Measurement**: Determine the space an element wants to occupy.
- **Layout**: Position itself and any children within a bounding region.
- **Rendering**: Draw itself to a target output surface, typically PDF.

These stages let every element participate in flexible, dynamic pagination and layout strategies.

Implementation classes track their own rendering state and may support multi-page output, internal content caching, or dynamic sizing behavior.

----

Automodule Documentation
------------------------

.. automodule:: kanji_time.visual.protocol.content
    :members:
    :undoc-members:
    :show-inheritance:
