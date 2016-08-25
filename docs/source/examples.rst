Examples
========


These are examples of how you might use this library


As an object with a filename:

.. code-block:: python

    import jsonstreams

    with jsonstreams.Stream('object', filename='foo') as f:
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
        with jsonstreams.Stream('array', fd=f) as s:
            s.write('foo')
            s.write('bar')
            with s.subobject() as b:
                b.write('foo', 'bar')
            with s.subarray() as b:
                b.write('x')
                b.write('y')
                b.write('z')
            s.write('oink')
