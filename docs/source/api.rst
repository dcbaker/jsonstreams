Public API
==========


Overview
--------

The main component is :py:class:`jsonstreams.Stream`, which provides the
interface for either an array or an object. The interfaces for this class
depend on whether it was initialized as an array or an object.


Exceptions
----------

.. py:exception:: JsonStreamsError(message)

    A base exception class for other JSONstreams errors.

    :param message: the message to be displayed with the exception is raised
    :type message: str (python 3) or unicode (python 2)


.. py:exception:: ModifyWrongStreamError(message)

    An exception raised when trying to modify on object within the stream which
    is not in focus.

    Because JSON is so strictly defined, and this module writes out all data
    into the stream immediately without building any intermediate data
    structures, it is impossible to write into a parent while a sub-stream is
    opened. This exception will be raised in that case.

    It is not advised to handle this exception, it is almost certainly a
    programming error.

    :param str message: the message to be displayed with the exception is raised

    .. code-block:: python

        with jsonstreams.Stream(Type.OBJECT, filename='foo') as s:
            with s.subobject('bar') as b:
                s.write('foo', 'bar')
        ModifyWrongStreamError


.. py:exception:: InvalidTypeError(message)

    An exception that is raised when an invalid type is passed for an argument.
    Primarily this will be raised from the :py:meth:`.Object.write` and
    :py:meth:`.Object.iterwrite` methods.

    JSON is pretty particularly about what kinds of values can be used as keys
    for objects, only text type is allowed, not lists, objects, null or numeric
    types. JSONstreams does not attempt to coerce values for the developer,
    instead it raises this exception.

    It is not advised to handle this exception, it is almost certainly a
    programming error.

    :param message: the message to be displayed with the exception is raised
    :type message: str (python 3) or unicode (python 2)

    .. code-block:: python

        with jsonstreams.Stream(Type.OBJECT, filename='foo') as s:
            with s.subobject(1) as b:
        InvalidTypeError

.. py:exception:: StreamClosedError(message)

    An exception that is raised when trying to write into an
    :py:class:`.Object` or :py:class:`.Array` after the close() method has
    already been called.

    :param message: the message to be displayed with the exception is raised
    :type message: str (python 3) or unicode (python 2)

    .. code-block:: python

        with jsonstreams.Stream(Type.OBJECT, filename='foo') as s:
            with s.subobject(1) as b:
                b.write('foo', 'bar)
            b.write('foo', 'bar)
        StreamClosedError



Classes
-------

.. py:class:: Type

    This is an enum that provides valid types for the Stream class.

    .. py:attribute:: OBJECT

        A JSON object

    .. py:attribute:: ARRAY

        A JSON array

    .. py:attribute:: object

        .. deprecated:: 0.6
            Use the OBJECT attribute instead.

        A JSON object

    .. py:attribute:: array

        .. deprecated:: 0.6
            Use the ARRAY attribute instead.

        A JSON array


.. py:class:: Stream(jtype, filename=none, fd=none, indent=0, pretty=false, encoder=json.JSONencoder)

    The stream class is the basic entry point for using JSONstreams, and is the
    only class meant to be instantiated directly. When initialized this class
    will add the methods of :py:class:`.Object` or :py:class:`.Array`, as
    matches the value of jtype.

    It can be initialized with either a filename, which it will open via
    :py:func:`open`, or a file-like object already opened for write, but not
    both. If it is passed a file-like object it will no longer close that
    object, it is the caller's job to do so.

    It also takes and indent argument, which will cause the writer to add the
    appropriate white space to the output. For especially large documents this
    may help decode, as some parsers have a limit on the number of characters
    per line.

    A pretty flag can be passed, which will further cause indents to be
    consistently written even for complex objects, which would normally not be
    set at the same base indent level as other objects. This can have a
    negative effect on performance.

    This class can also be used as a context manager (used with the with
    statement), which will automatically call the :py:meth:`.Stream.close`
    method when exiting the context.

    .. code-block:: python

        with jsonwriter.Stream(jsonstreams.Type.ARRAY, filename='foo') as s:
            s.write('foo')

    .. note::

        If the stream opens the file-like object itself by filename it will
        always close the file when the Stream is closed.

    .. warning::

        The behavior of close_fd will change in the future. Currently it
        defaults to True, but in JsonStreams 1.0 it will default to False.

    :arg Type jtype: A value of the :py:class:`.Type` enum.
    :keyword filename: If set this will be opened and the stream written into it.
    :type filename: str or None
    :keyword file fd: A file-like object defining a write and close method.
    :keyword int indent: The number of spaces before each level in the JSON document.
    :keyword bool pretty: Whether or not to indent complex objects.
    :keyword encoder: A callable that will create a json.JSONEncoder instance.
    :type encoder: json.JSONEncoder
    :keyword bool close_fd: Close the fd when the Stream closes. Ignored if passed a filename

    .. py:method:: write

        This method will differ in signature depending on whether jtype is
        Type.ARRAY or Type.OBJECT.

        If Type.ARRAY then this method is an alias for :py:meth:`.Array.write`.
        If Type.'object then this method is an alias for :py:meth:`.Object.write`.

    .. py:method:: iterwrite

        This method will differ in signature depending on whether jtype is
        Type.OBJECT or Type.ARRAY.

        If Type.ARRAY then this method is an alias for
        :py:meth:`.Array.iterwrite`.
        If Type.OBJECT then this method is an alias for
        :py:meth:`.Object.iterwrite`.

    .. py:method:: close

        This method will close the root object by calling either
        :py:meth:`.Object.close` or :py:meth:`.Array.close`, and will also
        close the file.

    .. py:method:: subobject

        This method will differ in signature depending on whether jtype is
        Type.OBJECT or Type.ARRAY.

        This method will open a new object in the stream by calling either
        :py:meth:`.Object.subobject` or :py:meth:`.Array.subobject`

    .. py:method:: subarray

        This method will differ in signature depending on whether jtype is
        Type.OBJECT or Type.ARRAY.

        This method will open a new array in the stream by calling either
        :py:meth:`.Object.subarray` or :py:meth:`.Array.subarray`


.. py:class:: Object

   The Object constructor is not considered a public API, and is not documented
   here because it is not guaranteed according to the `Semantic Versioning
   <http://semver.org>`_ standard. All other public methods, however are
   considered public API.

   This class represents an object in a JSON document. It provides as public
   API all of the methods necessary to write into the stream and to close it.
   Like the :py:class:`.Stream` it provides a context manager, and can be used
   as a context manager, including when called from the
   :py:meth:`.Object.subobject` or :py:meth:`.Array.subobject`.

   .. py:method:: subobject(key)

        Open a new sub-object within the current object stream.

        :param str key: When written this will be the key and the new object
                        will be the value
        :return: The sub-object instance.
        :rtype: :py:class:`.Object`
        :raises InvalidTypeError: if the key is not a str
        :raises ModifyWrongStreamError: if this stream is not the top of the stack
        :raises StreamClosedError: if :py:meth:`.Object.close` has been called

   .. py:method:: subarray(key)

        Open a new sub-array within the current object stream.

        :param str key: When written this will be the key and the new Array
                        will be the value
        :return: The sub-array instance.
        :rtype: :py:class:`.Array`
        :raises InvalidTypeError: if the key is not a str
        :raises ModifyWrongStreamError: if this stream is not the top of the stack
        :raises StreamClosedError: if :py:meth:`.Object.close` has been called

   .. py:method:: write(key, value)

        Write a key:value pair into the object stream.

        :param str key: The key value.
        :param value: The value to be written.
        :type value: Any type that can be encoded by the encoder argument of
                     :py:class:`.Stream`
        :raises InvalidTypeError: If the key is not str
        :raises ModifyWrongStreamError: if this stream is not the top of the stack
        :raises StreamClosedError: if :py:meth:`.Object.close` has been called

   .. py:method:: iterwrite(args)

        Write key:value pairs from an iterable.

        One should not use this for dumping a complete dictionary or list,
        unless doing transformations. This is intended to have a generator
        passed into it.

        .. code-block:: python

            with jsonstreams.Stream(Type.OBJECT, filename='foo') as s:
                s.iterwrite((str(s), s) for s in range(5))

        :param args: An iterator returning key value pairs
        :type value: An iterable of tuples where the key is str and the value
                     is any type that can be encoded by the encoder argument of
                     :py:class:`.Stream`
        :raises InvalidTypeError: If the key is not str
        :raises ModifyWrongStreamError: if this stream is not the top of the stack
        :raises StreamClosedError: if :py:meth:`.Object.close` has been called

    .. py:method:: close

        Close the current object.

        Once this is called any call to :py:meth:`write`,
        :py:meth:`iterwrite`, :py:meth:`subobject`, or
        :py:meth:`subarray` will cause an :py:class:`.StreamClosedError` to
        be raised.


.. py:class:: Array

   The Array constructor is not considered a public API, and is not documented
   here because it is not guaranteed according to the `Semantic Versioning
   <http://semver.org>`_ standard. All other public methods are considered
   public API.

   This class represents an array in a JSON document. It provides as public
   API all of the methods necessary to write into the stream and to close it.
   Like the :py:class:`.Stream` it provides a context manager, and can be used
   as a context manager, including when called from the
   :py:meth:`.Object.subarray` or :py:meth:`.Array.subarray`.

   .. py:method:: subobject()

        Open a new sub-object within the current array stream.

        :return: The sub-object instance.
        :rtype: :py:class:`.Object`
        :raises ModifyWrongStreamError: if this stream is not the top of the stack
        :raises StreamClosedError: if :py:meth:`.Object.close` has been called

   .. py:method:: subarray()

        Open a new sub-array within the current array stream.

        :return: The sub-array instance.
        :rtype: :py:class:`.Array`
        :raises ModifyWrongStreamError: if this stream is not the top of the stack
        :raises StreamClosedError: if :py:meth:`.Object.close` has been called

   .. py:method:: write(value)

        Write a value into the array stream.

        :param value: The value to be written.
        :type value: Any type that can be encoded by the encoder argument of
                     :py:class:`.Stream`
        :raises ModifyWrongStreamError: if this stream is not the top of the stack
        :raises StreamClosedError: if :py:meth:`.Object.close` has been called

   .. py:method:: iterwrite(args)

        Write values into an array from an iterator.

        One should not use this for dumping a complete list unless doing
        transformations. This is intended to have a generator passed into it.

        .. code-block:: python

            with jsonstreams.Stream(Type.OBJECT, filename='foo') as s:
                s.iterwrite(range(10, step=2))

        :param args: An iterator returning key value pairs
        :type value: An iterable of tuples where the key is str and the value
                     is any type that can be encoded by the encoder argument of
                     :py:class:`.Stream`
        :raises ModifyWrongStreamError: if this stream is not the top of the stack
        :raises StreamClosedError: if :py:meth:`.Object.close` has been called

    .. py:method:: close

        Close the current object.

        Once this is called any call to :py:meth:`write`,
        :py:meth:`iterwrite`, :py:meth:`subobject`, or
        :py:meth:`subarray` will cause an :py:class:`.StreamClosedError` to
        be raised.


.. vim: set textwidth=79 spell
