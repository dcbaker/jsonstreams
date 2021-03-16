Changes
=======

next
-----

0.6.0
------

New Features

- Internally use the JSONEncoder's `iterencode` rather than `encode` for memory
  efficiency.  This makes little difference for the default built-in `json`'s
  JSONEncoder, but a custom JSONEncoder that emits large objects in small output
  chunks can now pass this memory efficiency all the way through jsonstreams,
  allowing arbitrarily large elements to be emitted in bounded memory.
  (This is not yet implemented for pretty=True.)

Deprecation

- Type.array and Type.object have deprecated in favor of Type.ARRAY and
  Type.OBJECT, respectively. The former will be removed in version 1.0

Bug Fixes:

- Use the JSONEncoder.*_separator values instead of hard coded values
  (`#35 <https://github.com/dcbaker/jsonstreams/issues/35>`_)

0.5.0
------

Bug Fixes:

- Fix a bug that prevents the Stream class from producing proper compact JSON output
  (`#21 <https://github.com/dcbaker/jsonstreams/issues/21>`_)
- Add api to control closing the file-like object on Stream close
  (`#23 <https://github.com/dcbaker/jsonstreams/issues/23>`_)
- flush the fd before closing the Stream
  (`#24 <https://github.com/dcbaker/jsonstreams/issues/24>`_)

0.4.3
------

New Features

- Add support for Python 3.9
- Drop support for python 3.5

0.4.2
------

New Features

- Add support for Python 3.7 and 3.8
- Drop support for python 3.4


0.4.1
-----

New Features

- Bump from alpha to beta quailty. The public API will no longer change in a
  non-backwards compatible way without a very good reason.
- Add support for Python 3.6


0.4.0
-----

New Features:

- Use an enum rather than a string to set the object type in Stream.
  For python < 3.4 this adds a new requirement on enum34

Bug Fixes:

- Fix numerous typos and errors in the sphinx documentation


0.3.2
-----

New Features:

- Proper documentation via readthedocs


0.3.1
-----

New Features:

- Add __slots__ to the Writer classes

Bug Fixes:

- Fix a bug with both ObjectWriter and ArrayWriter with pretty printing, in
  which the comma property wouldn't be properly set.
  (`#12 <https://github.com/dcbaker/jsonstreams/issues/12>`_)
- Fix bug with ObjectWriter and pretty printing.
  (`#11 <https://github.com/dcbaker/jsonstreams/issues/11>`_)


0.3.0
-----

New features:

- Allow passing a filename or an already opened fd to the Stream class.
  (`#4 <https://github.com/dcbaker/jsonstreams/issues/4>`_)
- Add typing stub files. (`#6 <https://github.com/dcbaker/jsonstreams/issues/6>`_)
- Add iterwrite methods. These allow writing generators and iterators without
  creating an in memory data-structure.
  (`#8 <https://github.com/dcbaker/jsonstreams/issues/8>`_)


0.2.1
-----

Bug Fixes:

- Pass the pretty flag down in the Stream class correctly. This bug was more of
  an annoyance than anything else.
  (`#7 <https://github.com/dcbaker/jsonstreams/issues/7>`_)


0.2.0
-----

New features:

- Added a pretty printer flag. This allows printing complex object with the
  expected level of indent, but with added overhead.
  (`#3 <https://github.com/dcbaker/jsonstreams/issues/3>`_)

Bug Fixes:

- Pass the indent value to the encoder of the writer, which means complex
  objects get indented. The value may not be what is expected without the
  pretty flag.
  (`#2 <https://github.com/dcbaker/jsonstreams/issues/2>`_)
- Invalid types can no longer be passed as keys to Object.write.
  (`#1 <https://github.com/dcbaker/jsonstreams/issues/1>`_)


.. vim: textwidth=79
