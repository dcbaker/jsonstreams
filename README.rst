JSONStreams
===========


.. image:: https://travis-ci.org/dcbaker/jsonstreams.svg?branch=master
    :target: https://travis-ci.org/dcbaker/jsonstreams

.. image:: https://ci.appveyor.com/api/projects/status/4umkvc9thitacbf9/branch/master?svg=true
    :target: https://ci.appveyor.com/project/dcbaker/jsonstreams


Source code is available at github_.

The code is licensed MIT. See the included LICENSE file for the exact terms.


Description
###########

JSONstreams is a package that attempts to making writing JSON in a streaming
format easier. In contrast to the core json module, this package doesn't
require building a complete tree of dicts and lists before writing, instead it
provides a straightforward way to to write a JSON document **without** building
the whole data structure ahead of time.

JSONstreams considers there to be two basic types, the JSON array and the JSON
object, which correspond to Python's list and dict respectively, and can encode
any types that the json.JSONEncoder can, or can use an subclass to handle
additional types.

The interface is designed to be context manger centric. The Stream class, and
the Array and Object classes returned by the subarray and subobject methods
(respectively), can be used as context managers or not, but use as context
managers are recommended to ensure that each container is closed properly.


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
