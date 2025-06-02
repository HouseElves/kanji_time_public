"""Provide useful accessories for writing to XML-like files."""
# pylint: disable=fixme

from contextlib import contextmanager

# pylint: disable=wrong-import-position, wrong-import-order
import io
import logging
logger = logging.getLogger(__name__)


in_typeface = lambda face, text: f"<font face='{face}'>{text}</font>"  #: handle short typeface changes
in_bold = lambda text: f"<b>{text}</b>"  #: handle short boldface spans
in_italic = lambda text: f"<i>{text}</i>"  #: handle short italic spans


@contextmanager
def xml_tag(file_handle: io.TextIOBase, tag_name: str, **kwargs):
    """
    Manage an XML tag in a with-block, writing open and close tags automatically.

    Attributes can be passed via keyword arguments.
    All content written within the block is buffered and wrapped in the tag.

    :param file_handle: a text file opened for write
    :param tag_name: the start tag waiting for its companion end tag
    :param kwargs: ad hoc keyword arguments passed along into the opening tag as XML attributes.

    .. only:: dev_notes

        - what about my indent level |rarr| derive an "indented buffer" off `StringIO` or one of its chums.

    """
    # Code to acquire resource, e.g.:
    attributes = ', '.join(f'{k}="{v}"' for k, v in kwargs.items())
    with io.StringIO() as buffer:
        print(f"<{tag_name} {attributes}>", file=buffer)
        buffer.flush()
        try:
            yield buffer
        except Exception as e:
            logger.error("Unhandled exception %s while constructing tag '%s'", e, tag_name)
            print(f"Unhandled exception:  {e}.")
            raise e from e
        finally:
            print(f'</{tag_name}>', file=buffer)
            buffer.flush()
            file_handle.write(buffer.getvalue())
