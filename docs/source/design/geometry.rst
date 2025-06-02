==================================
How does the layout geometry work?
==================================

Layout in Kanji Time operates in a unit-aware 2D coordinate space, using value types to express physical dimensions, screen-relative
distances, and nested layout regions.

All elements are grounded in a shared system of immutable types:

  :class:`Distance`
        A scalar length with an extensive library of measurement units, attribute-level unit conversion, and soft constraint logic

  :class:`Pos`
        A position in 2D space used for frame origins and alignment. A :class:`Pos` is a pair of :class:`Distance` instances.

  :class:`Extent`
        A range of positions in 2D space of (0 to width) x (0 to height) used for sizing and layout negotiation.
        A :class:`Extent` is a pair of :class:`Distance` instances.

  :class:`Region`
        A rectangular area identified by an origin (a :class:`Pos`) and a size (an :class:`Extent`) used to scope layout frames in their own local coordinate system.

  :class:`AnchorPoint`
       A collection of symbolic compass-style labels for alignment hints when nesting geometery objects.

All these types support simple arithmetic methods appropriate to their semantic type.

Instances of the :class:`RenderingFrame` protocol pass around geometry objects during layout and render phases. These geometry object provide the backbone for all geometry-aware layout
strategies.

Each geometry class is derived from `namedtuple`, thus making them immutable, and extended with layout-specific operations such as anchoring, intersection, and scaling.


.. seealso::  See :ref:`Distance type enhancements <layout_and_geometry>` for raw notes about extending the Distance type.