from cache_tagging.utils import Undef

try:
    str = unicode  # Python 2.* compatible
    string_types = (basestring,)
    integer_types = (int, long)
except NameError:
    string_types = (str,)
    integer_types = (int,)


class RelationManager(object):

    class ITags(object):

        def parent(self):
            raise NotImplementedError

        def name(self):
            raise NotImplementedError

        def add(self, tags, version=None):
            raise NotImplementedError

        def values(self, version=None):  # TODO: rename to get()?
            raise NotImplementedError

    class Tags(ITags):

        def __init__(self, name, parent=None):
            self._name = name
            self._parent = parent
            self._tags = dict()

        def parent(self):
            return self._parent

        def name(self):
            return self._name

        def add(self, tags, version=None):
            if version not in self._tags:
                self._tags[version] = set()
            self._tags[version] |= set(tags)
            if self._parent is not None:
                self._parent.add(tags, version)

        def values(self, version=None):
            try:
                return self._tags[version]
            except KeyError:
                return set()

    class NoneTags(ITags):
        """Using pattern Special Case"""
        def __init__(self):
            pass

        def parent(self):
            return None

        def name(self):
            return 'NoneTags'

        def add(self, tags, version=None):
            pass

        def values(self, version=None):
            return set()

    def __init__(self):
        self._current = None
        self._data = dict()  # recursive cache is not possible, so, using dict instead of stack.

    def get(self, name):
        if name not in self._data:
            self._data[name] = self.Tags(name, self._current)
        return self._data[name]

    def pop(self, name):
        try:
            node = self._data.pop(name)
        except KeyError:
            node = self.NoneTags()

        if self.current() is node:
            self.current(node.parent())
        return node

    def current(self, name_or_node=Undef):
        if name_or_node is Undef:
            return self._current or self.NoneTags()
        if isinstance(name_or_node, string_types):
            node = self.get(name_or_node)
        else:
            node = name_or_node
        self._current = node

    def clear(self):
        self._data = dict()