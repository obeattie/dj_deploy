"""Miscellaneous utility functions."""

def flattened(seq):
    """Generator that 'flattens' the passed iterable. Useful for turning
       multi-dimensional sequences into single-dimensional ones while
       preserving item order ([1, [2, [3]]] would become [1, 2, 3]). Note
       that strings are not flattened to characters."""
    for item in seq:
        try:
            # Test if the item is iterable (TypeError is raised if not)
            iter(item)
            # String iteration = infinite recursion as the characters are themselves
            # strings, and therefore iterable too
            assert not isinstance(item, basestring)
            for subitem in flattened(item):
                yield subitem
        except (TypeError, AssertionError):
            yield item

def uniquified(seq):
    """Generator that 'uniquifies' the passed iterable. Note that this
       generator is not particularly memory-efficient. Each item is
       stored in a temporary list once it has been asked for until the
       end of the iterable is reached. Thus, if the input is a generator,
       memory usage will go up."""
    hits = []
    for item in seq:
        if not item in hits:
            hits.append(item)
            yield item
