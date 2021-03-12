Examples
========


These are examples of how you might use this library


Basic
-----

As an object with a filename:

.. code-block:: python

    import jsonstreams

    with jsonstreams.Stream(jsonstreams.Type.OBJECT, filename='foo') as f:
        f.write('foo', 1)
        with f.subobject('bar') as b:
            b.iterwrite((str(s), s) for s in range(5))
        with f.subarray('oink') as b:
            b.write('foo')
            b.write('bar')
            b.write('oink')


As an array with an fd:

.. code-block:: python

    import bz2

    import jsonstreams
       
    with bz2.open('foo') as f:
        with jsonstreams.Stream(jsonstreams.Type.ARRAY, fd=f) as s:
            s.write('foo')
            s.write('bar')
            with s.subobject() as b:
                b.write('foo', 'bar')
            with s.subarray() as b:
                b.write('x')
                b.write('y')
                b.write('z')
            s.write('oink')


Customizing the encoder
-----------------------

The encoder can be customized to allow complex types to be passed in without
having to convert them into types that json.JSONEncoder can natively
understand. It can be done by subclassing the JSONEncoder, but this isn't
recommended by simplejson, instead it is better to pass a function to the
:py:meth:`json.JSONencoder`'s default parameter. This is easily achieved by
using a :py:func:`functools.partial`.

.. warning::

    It is critical that you do not pass a value for indent, as the
    :py:class:`.Stream` class sets this value internally.


.. code-block:: python

    from functools import partial
    from json import JSONEncoder

    def my_encoder(self, obj):
        # Turn sets into lists so they can be encoded
        if isinstance(obj, set):
            return list(obj)
        return obj

    with jsonstreams.Stream(jsonstreams.Type.OBJECT, filename='foo',
                            encoder=partial(JSONEncoder, default=my_encoder)):
        s.write('foo', {'foo', 'bar'})
