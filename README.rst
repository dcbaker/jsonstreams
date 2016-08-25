JSONStreams
===========


.. image:: https://travis-ci.org/dcbaker/jsonstreams.svg?branch=master
    :target: https://travis-ci.org/dcbaker/jsonstreams

.. image:: https://ci.appveyor.com/api/projects/status/ocrt9nol8kn3pm1t/branch/master?svg=true
    :target: https://ci.appveyor.com/project/dcbaker/jsonstreams


Source code is available at github_.

The code is licensed MIT. See the included LICENSE file for the exact terms.


Description
###########

.. include:: docs/source/description.rst


Basic Usage
###########

A simple use looks like this::
    
    with jsonstreams.Stream('foo', 'object') as s:
        s.write('foo', 'bar')
        with s.subobject('a') as a:
            a.write(1, 'foo')
            a.write(2, 'bar')
        s.write('bar', 'foo')

Writing into a closed group will raise an exception, which should not be
handled, this exception is always an error in programming and should be
corrected.

It is possible to write any value that the encoder (json.JSONEncoder by
default) can encode, so iterating over lists or dictionaries to write them in
is unnecessary::

    mylist = list(range(10))
    mydict = {a, b, for a in range(10), for b in 'abcdefghij'}

    with jsonstreams.Stream('foo', 'object') as s:
        s.write('list', mylist)
        s.write('dict', mydict)


.. _github: https://github.com/dcbaker/jsonstreams
