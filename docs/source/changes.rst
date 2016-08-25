Changes
=======

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

- Added a pretty printer flag. This allows priting complex object with the
  expected level of indent, but with added overhread. 
  (`#3 <https://github.com/dcbaker/jsonstreams/issues/3>`_)

Bug Fixes:

- Pass the indent value to the encoder of the writer, which means complex
  objects get indented. The value may not be what is expected without the
  pretty flag.
  (`#2 <https://github.com/dcbaker/jsonstreams/issues/2>`_)
- Invalid types can no longer be passed as keys to Object.write.
  (`#1 <https://github.com/dcbaker/jsonstreams/issues/1>`_)


.. vim: textwidth=79
