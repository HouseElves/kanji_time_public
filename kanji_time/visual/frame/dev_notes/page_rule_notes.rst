:orphan:

.. _page_rule.py.dev_notes:

==============================
page_rule.py Development Notes
==============================

For: :mod:`visual.frame.page_rule`

.. include:: /common

Future Feature Adds
-------------------

Layouts
~~~~~~~

    - for completeness, I need a "vertical" version of :python:`frame.page_rule.HorizontalRule` - reuse the `StackLayoutStrategy` orientation parameter
    - to be considered a "rule", a `HorizontalRule` frame must span the entire width of the parent container.
      Arguably, a page rule should be considered a part of the layout strategy or a container attribute ("add rule separators" N/S/E/W?).
      In this scenario, thr `HorizontalRule` class becomes a "line" drawing element?  Maybe?

Documentation, Code, Push guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - do I need documentation style rules about what properties go into the Mermaid class diagram:  just @property or all self data?

        - my thoughts are "as appropriate" to the diagram, no hard and fast rules beyond "use your best judgement".

    - convert my template RST to a list of approved dev_notes headings and in the correct order
    - consider # NOTE for automatic dev_note extraction from code and consolidation to the module/class/function header.
    - Anything that I can do to automate dev_note consolidation is a good thing.
      # NOTE[<heading/type>] comes to mind.

        - Examples:  NOTE[Review], NOTE[Factor], NOTE[New Features/Whitespace strategies]

    - Change NOTE to NOTED after extraction?
    - Can I link this up with a ticketing / PM system with Jira or Jira-light or Github or MSFT Tasks?

Testing / Hygeine Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    - Require 100% branch coverage tests for a push to be accepted
    - Require a clean PyLint w/ documented "# pylint: disable=" ccomments


Code Review/Adjustments
-----------------------

    - Nomenclature: The :python:`frame.HorizontalRule` initializer should  have requested_size parameter, not size, for consistency.
    - Review: why does :python:`frame.HorizontalRule` have a measure() method instead of letting `SimpleElement` do the work?



