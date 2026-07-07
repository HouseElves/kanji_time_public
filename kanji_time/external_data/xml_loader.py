from dataclasses import field, make_dataclass, dataclass
from typing import Any, Generic, Protocol, Self, TypeVar, runtime_checkable
from collections.abc import Callable, Mapping, MutableMapping, Sequence
from collections import namedtuple
import xml.etree.ElementTree as et
from functools import cached_property

from kanji_time.utilities.class_property import classproperty


T = TypeVar('T')
Factory = Callable[..., T]


class BetterQName(et.QName):
    """Isolate the namespace in a qualified name of the form "{uri}tag"."""

    def __init__(self, text_or_uri: str, tag:str = None):
        self._namespace: slice = slice(0, 0)
        self._tag: slice = slice(0, len(tag or text_or_uri))
        if tag:
            self._namespace = slice(1, len(text_or_uri) + 1)
            self._tag = slice(len(text_or_uri) + 2, None)
        elif text_or_uri[0] == '{':
            rb_index = text_or_uri.rfind('}', 1)
            if rb_index > 0:
                self._namespace = slice(1, rb_index)
                self._tag = slice(rb_index + 1, None)
        super().__init__(text_or_uri, tag)

    @property
    def namespace(self):
        return self.text[self._namespace]

    @property
    def tag(self):
        return self.text[self._tag]

assert BetterQName("foo").namespace == ""
assert BetterQName("foo").tag == "foo"
assert BetterQName("{foo").namespace == ""
assert BetterQName("{foo").tag == "{foo"
assert BetterQName("{}foo").namespace == ""
assert BetterQName("{}foo").tag == "foo"
assert BetterQName("{foo}").namespace == "foo"
assert BetterQName("{foo}").tag == ""
assert BetterQName("foo", "bar").namespace == "foo"
assert BetterQName("foo", "bar").tag == "bar"
assert BetterQName(BetterQName("foo", "bar").namespace, BetterQName("foo", "bar").tag) == BetterQName("foo", "bar")


@runtime_checkable
class TagMetadata(Protocol):
    """
    Model the content of an XML DTD for a particular tag independent of namespaces.

    This model is incomplete and super simple - yet exactly enough to do what I need.

    The TagMetadata describes its instance data as properties to allow implementors freedom to 
    represent them as they see fit.

        *tag_name* - the unqualified name of the XML tag as given in <!ELEMENT *tag_name* ... >
        
        *attributes* - the unqualified names of the XML tag's attributes as given in <!ATTLIST *tag_name* *attr_name* *attr_type* *attr_dflt* *attr_name* *attr_type* *attr_dflt* ... >

        *children* - the unqualified name of a the XML tag's child entities as given in <!ELEMENT *tag_name* (*child_name* ...)>
    """
    @property
    def tag_name(self) -> str:
        """Expose the unqualified name of the described XML tag."""
        ...

    @property
    def attributes(self) -> Sequence[str]:
        """Expose the unqualified attribute names for the described XML tag."""
        ...

    @property
    def children(self) -> Sequence[str]:
        """Expose the unqualified child tag names for the described XML tag."""
        ...

    @property
    def tag_factory(self) -> Factory[T]:
        """Provide a construction function for classes containing instances of the type described by this metadata."""
        ...

    @property
    def continuation(self) -> Self | None:
        """Link source metadata when this metadata is a refinement of other metadata."""
        ...


@dataclass 
class TagSymbol:
    namespace: str
    name: str
    metadata: TagMetadata


FrozenSymbolTable = Mapping[str, TagSymbol]


class TagFactory(Generic[T]):
    """
    Make tag instances using metadata provided at run time.
    
    T is the type holding the tag instance data.
    """

    symbols: FrozenSymbolTable

    @property
    def metadata(self):
        return self._metadata

    def __init__(self, metadata: TagMetadata, tag_base: type[T]):
        """Initialized a tag instance factory from its corresponding DTD metadata."""
        self._metadata = metadata
        # A tag instance is a dataclass with string fields for the attributes derived from a custom base.
        # The TagInstance base is defined later - I'm aliasing it with a typevar T & passing in its type to avoid circular dependency issues.
        fields = [
            (attribute, str, field(default=''))
            for attribute in metadata.attributes
            ]
        self.tag_class = make_dataclass(
            metadata.tag_name, 
            fields, 
            bases=(tag_base,)
            )

    def from_element(self, element: et.Element) -> T:
        """
        Create a tag instance from data in an ElementTree.Element instance.

        It's redundant work, I'm bootstrapping from ElementTree first.
        """
        namespace = self.symbols[self.metadata.tag_name].namespace
        attributes = {
            qname.tag: value
            for (qname, value) in [(BetterQName(k), v) for (k, v) in element.items()]
            if qname.namespace == namespace
            }
        return self.tag_class(**attributes)

    def __call__(self, *args, **kwargs) -> T:
        """Create a tag instance using its constructor function."""
        return self.tag_class(*args, **kwargs)


class TagInstance:
    """Provide a common root class for different dataclass representations of XML tags."""

    def __init_subclass__(cls, /, factory, **kwargs):    
        super().__init_subclass__(**kwargs)
        cls._factory = factory
        cls._child_tag_instances: dict[str, Self] = {}

    @classproperty
    def factory(self) -> TagFactory[Self]:
        return self._factory
    
    @classproperty
    def metadata(cls) -> TagMetadata:
        return cls.factory.metadata

    @classmethod
    def from_element(cls, namespaces: Mapping[str, str], element: et.Element):
        """
        Construct an instance of this dataclass from an XML element's attributes.

        :param element: the XMK element instance to scan for attributes in my namespace.
        """
        return cls(**dict((cls.attrib_namespace.get(a, a), b) for (a, b) in element.items()))
    
    @classmethod
    def child_from_element(cls, namespaces, child_element: et.Element):
        factory = cls._child_factories.get(child_element.tag, None)
        if factory is None and child_element.tag in cls.metadata.children:
            cls._child_factories[child_element.tag] = (factory := cls.metadata.create_tag_factory())
        assert factory is not None



def create_tag_factory(metadata: TagMetadata) -> Factory[TagInstance]:
        
    fields = [
        (attribute, str, field(default=''))
        for attribute in metadata.attributes
    ]

    dc = make_dataclass(
        metadata.tag_name, 
        fields, 
        bases=(TagInstance,)
    )

    def factory(*args, **kwargs):
        instance = dc(*args, **kwargs)
        instance._metadata = metadata
        return instance

    return factory


class BaseTagMetadata(TagMetadata):
    """
    Define a simple-as-possible model of an XML tag & its descendants all having a common namespace.

    The namespace is defined *externally* to the to the tag description.

    TODO: Sequence[str] is wrong.  Should be a ImmutableSequence 

    :param tag_name: as in :class:`TagMetadata`.
    :param attributes: as in :class:`TagMetadata`.
    :param children: as in :class:`TagMetadata`.    
    """

    def __init__(self, tag_name: str, attributes: Sequence[str], children: Sequence[str]):
        """Initialize a new simple tag metadata analogously to its DTD description."""
        self._tag_name = tag_name
        self._attributes = attributes
        self._children = children

    @property
    def tag_name(self) -> str:
        """Define the *tag_name* as its internal string representation."""
        return self._tag_name

    @property
    def attributes(self) -> Sequence[str]:
        """Define the *attributes* as its internal [string] representation."""
        return self._attributes

    @property
    def children(self) -> Sequence[str]:
        """Define the *tag_name* as its internal [string] representation."""
        return self.children


class XMLRestrictedTagMetadata(TagMetadata):
    """Model a known XML tag with limited subset of its attributes or children."""

    def __init__(self, parent: TagMetadata, attribute_subset: Sequence[str], child_subset: Sequence[str]):
        self.parent = parent
        self._attributes = list(set(parent.attributes) & set(attribute_subset))
        self._children = list(set(parent.children) & set(child_subset))

    @property
    def tag_name(self) -> str:
        return self.parent.tag_name

    @property
    def attributes(self) -> Sequence[str]:
        return self._attributes

    @property
    def children(self) -> Sequence[str]:
        return self._children


class XMLExtendedTagMetadata(TagMetadata):
    """
    Model a known XML tag with an enhanced superset of its attributes or children.

    When assigning namespaces. an extended tag should live in a distinct namespace from its known parent.
    """

    def __init__(self, parent: TagMetadata, attributes_added: Sequence[str], children_added: Sequence[str]):
        self.parent = parent
        self._attributes = list(set(parent.attributes) | set(attributes_added))
        self._children = list(set(parent.children) | set(children_added))

    @property
    def tag_name(self) -> str:
        return self.parent.tag_name

    @property
    def attributes(self) -> Sequence[str]:
        return self._attributes

    @property
    def children(self) -> Sequence[str]:
        return self._children







