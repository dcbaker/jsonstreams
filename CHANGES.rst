Changes
=======

0.2.1
----

Bug Fixes:

- Pass the pretty flag down in the Stream class correctly. This bug was more of
  an annoyance than anything else. 
  (`#7 https://github.com/dcbaker/jsonstreams/issues/7`)


0.2.0
-----

New features:

- Added a pretty printer flag. This allows priting complex object with the
  expected level of indent, but with added overhread. 
  (`#3 https://github.com/dcbaker/jsonstreams/issues/3`)

Bug Fixes:

- Pass the indent value to the encoder of the writer, which means complex
  objects get indented. The value may not be what is expected without the
  pretty flag.
  (`#2 https://github.com/dcbaker/jsonstreams/issues/2`)
- Invalid types can no longer be passed as keys to Object.write.
  (`#1 https://github.com/dcbaker/jsonstreams/issues/1`)
