# encoding=utf-8
# Copyright © 2016 Dylan Baker

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""A streaming JSON writing library.

JSON streams provides a simple, object oriented, interface for writing JSON
data as a stream, without building a complex data tree first. This is
advantageous when working with particularly large data sets that would consume
a lot of memory to build out completely, or when using systems with constrained
memory.

The interface is designed to be as safe as possible, and provides context
manager interfaces to maximize this safety.

Basic usage:

Create a Stream instance, which will be either an object (in JSON terminology,
dict in python terminology), or an array (list in python terminology). Then use
the write method to write elements into the file.

>>> with Stream('foo', 'array') as s:
...     s.write('foo')
...     s.write('bar')

Each element can also open a subelement, either via the subarray() or
subobject() method.

>>> with Stream('foo', 'array') as s:
...     s.write('foo')
...     with s.subobject() as o:
...         o.write(1, 'bar')

Any object that can be serialized can be passed (although passing some elements
as object keys is not supported, and should not be passed).

>>> with Stream('foo', 'object') as s:
...     s.write('foo', {'foo': 'bar'})

It is very important to note that while the Array and Object classes present
the same API, the signature of their write methods is necessarily different.
For Array, it accepts a single element, for Object it requires two elements,
the key and the value.
"""

import copy
import functools
try:
    import simplejson as json
except ImportError:
    import json

__all__ = [
    'Stream',
]

__version__ = '0.1.2'


class JSONStreamsError(Exception):
    """Base exception for jsonstreams."""


class StreamClosedError(JSONStreamsError):
    """Error raised when writing into a closed Element."""


class BaseWriter(object):
    """Private class for writing things."""

    def __init__(self, fd, indent, baseindent, encoder):
        self.fd = fd  # pylint: disable=invalid-name
        self.indent = indent
        self.baseindent = baseindent
        self.encoder = encoder

        self.write = self._write_no_comma

        if indent:
            self.write_comma_literal = functools.partial(
                self.raw_write, ',', newline=True)
        else:
            self.write_comma_literal = functools.partial(self.raw_write, ', ')

    @property
    def comma(self):
        return self.write == self._write_comma

    def _indent(self):
        return ' ' * self.baseindent * self.indent

    def raw_write(self, value, indent=False, newline=False):
        if indent:
            self.fd.write(self._indent())
        self.fd.write(value)
        if newline:
            self.fd.write('\n')

    def _write_no_comma(self):
        """Baseish class."""

    def _write_comma(self):
        """Baseish class."""

    def set_comma(self):
        # replace with the comma version, removeing the need for extra if
        # statements.
        self.write = self._write_comma


class ObjectWriter(BaseWriter):
    """A Writer class specifically for Objects.

    Supports writing keys and values.
    """

    def write_key(self, key):
        self.raw_write(self.encoder.encode(key), indent=self.indent)
        self.raw_write(': ')

    def _write_no_comma(self, key, value):  # pylint: disable=arguments-differ
        """Write without a comma."""
        self.write_key(key)
        self.raw_write(self.encoder.encode(value))

        # replace with the comma version, removeing the need for extra if
        # statements.
        self.write = self._write_comma

    def _write_comma(self, key, value):  # pylint: disable=arguments-differ
        """Write with a comma."""
        self.write_comma_literal()
        self.write_key(key)
        self.raw_write(self.encoder.encode(value))


class ArrayWriter(BaseWriter):
    """Writer for Arrays.

    Supports writing only values.
    """

    def _write_no_comma(self, value):  # pylint: disable=arguments-differ
        """Write without a comma."""
        self.raw_write(self.encoder.encode(value), indent=self.indent)
        self.set_comma()

    def _write_comma(self, value):  # pylint: disable=arguments-differ
        """Write with a comma."""
        self.write_comma_literal()
        self.raw_write(self.encoder.encode(value), indent=self.indent)


def _raise(exc, *args, **kwargs):  # pylint: disable=unused-argument
    """Helper to raise an exception."""
    raise exc


class Open(object):
    """A helper to allow subelements to be used as context managers."""

    def __init__(self, initializer):
        self.__inst = initializer()
        self.close = self.__inst.close
        self.subarray = self.__inst.subarray
        self.subobject = self.__inst.subobject

    def write(self, *args, **kwargs):
        self.__inst.write(*args, **kwargs)

    def __enter__(self):
        return self.__inst

    def __exit__(self, etype, evalue, traceback):
        self.__inst.close()


class Object(object):
    """A streaming array representation."""

    def __init__(self, fd, indent, baseindent, encoder, _indent=False):
        self._writer = ObjectWriter(fd, indent, baseindent, encoder)
        self._writer.raw_write('{', indent=_indent, newline=indent)
        self._writer.baseindent += 1

    def _sub(self, jtype, key):
        if self._writer.comma:
            self._writer.write_comma_literal()
        self._writer.set_comma()
        self._writer.write_key(key)
        return Open(functools.partial(
            jtype, self._writer.fd, self._writer.indent,
            self._writer.baseindent, self._writer.encoder, _indent=False))

    def subobject(self, key):  # pylint: disable=method-hidden
        return self._sub(Object, key)

    def subarray(self, key):  # pylint: disable=method-hidden
        return self._sub(Array, key)

    def write(self, key, value):  # pylint: disable=method-hidden
        return self._writer.write(key, value)

    def close(self):  # pylint: disable=method-hidden
        """Close the Object.

        Once this method is closed calling any of the public methods will
        result in an StreamClosedError being raised.
        """
        if self._writer.indent:
            self._writer.raw_write('\n')
        self._writer.baseindent -= 1
        self._writer.raw_write('}', indent=True)

        self.write = functools.partial(
            _raise, StreamClosedError('Cannot write into a closed object!'))
        self.close = functools.partial(
            _raise,
            StreamClosedError('Cannot close an already closed object!'))
        self.subarray = functools.partial(
            _raise,
            StreamClosedError('Cannot open a subarray of a closed object!'))
        self.subobject = functools.partial(
            _raise,
            StreamClosedError('Cannot open a subobject of a closed object!'))

    def __enter__(self):
        return self

    def __exit__(self, etype, evalue, traceback):
        self.close()


class Array(object):
    """A streaming array representation."""

    def __init__(self, fd, indent, baseindent, encoder, _indent=False):
        self._writer = ArrayWriter(fd, indent, baseindent, encoder)
        self._writer.raw_write('[', indent=_indent, newline=indent)
        self._writer.baseindent += 1

    def _sub(self, jtype):
        if self._writer.comma:
            self._writer.write_comma_literal()
        self._writer.set_comma()
        return Open(functools.partial(
            jtype, self._writer.fd, self._writer.indent,
            self._writer.baseindent, self._writer.encoder, _indent=True))

    def subobject(self):  # pylint: disable=method-hidden
        return self._sub(Object)

    def subarray(self):  # pylint: disable=method-hidden
        return self._sub(Array)

    def write(self, value):  # pylint: disable=method-hidden
        return self._writer.write(value)

    def close(self):  # pylint: disable=method-hidden
        """Close the Object.

        Once this method is closed calling any of the public methods will
        result in an StreamClosedError being raised.
        """
        if self._writer.indent:
            self._writer.raw_write('\n')
        self._writer.baseindent -= 1
        self._writer.raw_write(']', indent=True)

        self.write = functools.partial(
            _raise, StreamClosedError('Cannot write into a closed array!'))
        self.close = functools.partial(
            _raise,
            StreamClosedError('Cannot close an already closed array!'))
        self.subarray = functools.partial(
            _raise,
            StreamClosedError('Cannot open a subarray of a closed array!'))
        self.subobject = functools.partial(
            _raise,
            StreamClosedError('Cannot open a subobject of a closed array!'))

    def __enter__(self):
        return self

    def __exit__(self, etype, evalue, traceback):
        self.close()


class Stream(object):
    """A JSON stream object.

    This object is the "root" object for the stream. It handles opening and
    closing the file, and provides the ability to write into the stream, and to
    open sub elements.

    This element can be used as a context manager, which is the recommended way
    to use it.

    Arguments:
    filename -- the name of the file to open
    jtype    -- either 'object' or 'array', this will set the type of the
                stream's root.

    Keyword Arguments:
    indent   -- How much to indent each level, if set to 0 no indent will be
                used and the stream will be written in a single line.
                Default: 0
    encoder  -- A json.JSONEncoder instance. This will be used to encode
                objects passed to the write method of the Stream and all
                instances returned by the subarray and subobject methods of
                this instance and it's children.
                Default: json.JSONEncoder
    """

    _types = {
        'object': Object,
        'array': Array,
    }

    def __init__(self, filename, jtype, indent=0, encoder=json.JSONEncoder):
        """Constructor."""
        assert jtype in ['object', 'array']

        self.filename = filename
        self.__fd = open(filename, 'w')
        self.__inst = self._types[jtype](
            self.__fd, indent, 0, encoder())

        self.subobject = self.__inst.subobject
        self.subarray = self.__inst.subarray

    def write(self, *args, **kwargs):
        """Write values into the stream.

        This method wraps either Object.write or Array.write, depending on
        whether it was initialzed with the 'object' argument or the 'array'
        argument.
        """
        self.__inst.write(*args, **kwargs)

    def close(self):
        """Close the root element and the file."""
        self.__inst.close()
        self.__fd.close()

    def __enter__(self):
        """Start context manager."""
        return self

    def __exit__(self, etype, evalue, traceback):
        """Exit context manager."""
        self.close()
