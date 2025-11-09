"""
Sphinx extension to make section IDs unique across documents.

This extension prepends the document path to auto-generated section IDs,
ensuring uniqueness in singlehtml builds without changing heading text.

Installation:
    1. Copy this file to your Sphinx project (e.g., docs/_ext/unique_section_ids.py)
    2. Add to conf.py:
        sys.path.insert(0, os.path.abspath('./_ext'))
        extensions = [..., 'unique_section_ids']

Configuration (optional):
    # In conf.py
    unique_section_ids_separator = '-'  # Default separator
    unique_section_ids_exclude = []     # List of docnames to skip

LLM Disclosure: 
    - Initial code generated with Anthropic Claude Sonnet 4.5 
    - Tweaked using OpenAI ChatGPT 5
    - Reviewed and hand-edited to fit to purpose.
"""

from pathlib import Path
from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)


def normalize_doc_path(filepath: str, source_dir: str = None) -> str:
    """
    Convert an absolute file path to a relative document path without extension.
    
    Args:
        filepath: Full path like '/home/user/project/docs/code_stubs/settings_notes.rst'
        source_dir: Sphinx source directory (docs/ or similar). If None, attempts to detect.
    
    Returns:
        Relative path without extension like 'code_stubs/settings_notes'
    
    Examples:
        >>> normalize_doc_path('/project/docs/code_stubs/dev_notes/settings_notes.rst')
        'code_stubs/dev_notes/settings_notes'
    """
    if not filepath:
        return ""
    
    # Convert to Path object
    path = Path(filepath)
    
    # Remove file extension
    path_no_ext = path.with_suffix('')
    
    # Try to find 'docs' or common source directory in path
    parts = path_no_ext.parts
    
    # Look for common Sphinx source directory names
    source_markers = ['docs', 'doc', 'source', 'documentation']
    
    # Find the source directory in the path
    source_idx = None
    for i, part in enumerate(parts):
        if part in source_markers:
            source_idx = i
            break
    
    if source_idx is not None:
        # Return path relative to source directory
        relative_parts = parts[source_idx + 1:]
        return '/'.join(relative_parts)
    
    # If no source directory found, just use the filename without extension
    return path_no_ext.name


def node_to_filepath(node: nodes.Node) -> str:
    """
    Return the source file path associated with a doctree node.

    Walks up the parent chain until a node with a non-None .source is found.
    Falls back to the Sphinx environment if available via node.document.settings.env.

    Return
    ------
    str
        Absolute or project-relative path of the file containing this node,
        or an empty string if it cannot be determined.
    """
    # Case 1: direct source on this node or ancestor
    current = node
    while current is not None:
        src = getattr(current, "source", None)
        if src:
            return src
        current = getattr(current, "parent", None)

    # Case 2: fallback to Sphinx environment (when available)
    doc = getattr(node, "document", None)
    if doc is not None:
        settings = getattr(doc, "settings", None)
        if settings is not None:
            env = getattr(settings, "env", None)
            if env is not None:
                # use the document name and map it to a file path
                docname = getattr(env, "docname", None)
                if not docname and hasattr(env, "temp_data"):
                    docname = env.temp_data.get("docname")
                if docname:
                    try:
                        return env.doc2path(docname)
                    except Exception:
                        pass

    # Case 3: unknown
    return ""


def make_unique_section_id(docname: str, original_id: str, separator: str = '-') -> str:
    """
    Create a unique section ID by prepending document path.
    
    Args:
        docname: Document name (e.g., 'code_stubs/dev_notes/settings_notes')
        original_id: Original auto-generated ID (e.g., 'code-review-adjustments')
        separator: Character to use as separator (default: '-')
    
    Returns:
        Unique ID (e.g., 'code-stubs-dev-notes-settings-notes-code-review-adjustments')
    """
    # Convert docname path separators to hyphens
    doc_prefix = docname.replace('/', separator).replace('\\', separator)
    
    # Combine with original ID
    unique_id = f"{doc_prefix}{separator}{original_id}"
    
    return unique_id


def process_section_ids(app: Sphinx, doctree: nodes.document, docname: str):
    """
    Process all section nodes in the doctree to make their IDs unique.
    
    This is called on the 'doctree-resolved' event, after IDs have been
    auto-generated but before HTML is written.
    """
    # Get configuration
    separator = app.config.unique_section_ids_separator
    exclude = app.config.unique_section_ids_exclude or []
    source_dir = app.config.source_dir if hasattr(app.config, 'source_dir') else ""
    
    # Skip excluded documents
    if docname in exclude:
        logger.debug(f"Skipping section ID processing for excluded document: {docname}")
        return
    
    # Find all section nodes
    section_count = 0
    for node in doctree.traverse(nodes.section):
        # Get the current IDs
        old_ids = node['ids']
        
        if not old_ids:
            continue
        
        # Make each ID unique by prepending document path
        node_file = normalize_doc_path(node_to_filepath(node), source_dir) or docname
        new_ids = []
        for old_id in old_ids:
            new_id = make_unique_section_id(node_file, old_id, separator)
            new_ids.append(new_id)
        
        # Replace the IDs
        node['ids'] = new_ids
        
        # Also update any direct references to this node
        # (though Sphinx usually handles this automatically)
        if 'names' in node:
            # Keep the names unchanged - only IDs change
            pass
        
        section_count += 1
    
    if section_count > 0:
        logger.debug(f"Made {section_count} section IDs unique in document: {docname}")


def setup(app: Sphinx):
    """
    Sphinx extension setup function.
    """
    # Add configuration values
    app.add_config_value('unique_section_ids_separator', '-', 'html')
    app.add_config_value('unique_section_ids_exclude', [], 'html')
    
    # Connect to the doctree-resolved event
    # This fires after the doctree is built but before output is written
    app.connect('doctree-resolved', process_section_ids)
    
    return {
        'version': '1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }