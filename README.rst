JSONStreams
===========

.. image:: https://github.com/dcbaker/jsonstreams/workflows/lint/badge.svg
    :alt: Python Linting status

.. image:: https://github.com/dcbaker/jsonstreams/workflows/Unit%20tests/badge.svg
    :alt: Linux test status

.. image:: https://badge.fury.io/py/jsonstreams.svg
    :target: https://badge.fury.io/py/jsonstreams

.. image:: https://ci.appveyor.com/api/projects/status/ocrt9nol8kn3pm1t/branch/main?svg=true
    :target: https://ci.appveyor.com/project/dcbaker/jsonstreams
    :alt: Appveyor CI Status

.. image:: https://readthedocs.org/projects/jsonstreams/badge/?version=latest
    :target: http://jsonstreams.readthedocs.io/en/stable/?badge=latest
    :alt: Documentation Status


Source code is available at `github <https://github.com/dcbaker/jsonstreams>`_.

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

A simple example looks like this

.. code-block:: python

    import jsonstreams

    with jsonstreams.Stream(jsonstreams.Type.OBJECT, filename='foo') as s:
        s.write('foo', 'bar')
        with s.subobject('a') as a:
            a.write('foo', 1)
            a.write('bar', 2)
        s.write('bar', 'foo')

Writing into a closed group will raise an exception, which should not be
handled, this exception is always an error in programming and should be
corrected.

It is possible to write any value that the encoder (json.JSONEncoder by
default) can encode, so iterating over lists or dictionaries to write them in
is unnecessary:

.. code-block:: python

    import jsonstreams

    mylist = list(range(10))
    mydict = {a: b for a in range(10) for b in 'abcdefghij'}

    with jsonstreams.Stream(jsonstreams.Type.OBJECT, filename='foo') as s:
        s.write('list', mylist)
        s.write('dict', mydict)
