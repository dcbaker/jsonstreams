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


class JSONStreamsError(Exception):
    """Base exception for jsonstreams."""


class StreamClosedError(JSONStreamsError):
    """Error raised when writing into a closed Element."""


def _raise(exc, *args, **kwargs):  # pylint: disable=unused-argument
    """helper to raise an exception."""
    raise exc


class Open(object):
    """A helper to allow subelements to be used as context managers."""

    def __init__(self, initializer, writer=None, key=None):
        if writer:
            assert key is not None
            writer(key)

        self.__inst = initializer()
        self.write = self.__inst.write
        self.close = self.__inst.close
        self.subarray = self.__inst.subarray
        self.subobject = self.__inst.subobject

    def __enter__(self):
        return self.__inst

    def __exit__(self, etype, evalue, traceback):
        self.__inst.close()


class Object(object):
    """A streaming array representation."""

    def __init__(self, fd, indent, baseindent, encoder, _indent=True):
        self.__fd = fd
        self.__indent = indent
        self.__baseindent = copy.copy(baseindent)
        self.__write('{', indent=_indent, newline=self.__indent)
        self.__baseindent += 1
        self.__encoder = encoder

        # This does a rather clever hack to make the comma write free of ifs
        # using polymorphism. Basically after the method below writes, and then
        # replaces it self with a version that adds a comma.
        self.write = self.__write_no_comma

        self.subobject = functools.partial(
            Open,
            functools.partial(Object, self.__fd, self.__indent,
                              self.__baseindent, self.__encoder, False),
            self.__write_key)

        self.subarray = functools.partial(
            Open,
            functools.partial(Array, self.__fd, self.__indent,
                              self.__baseindent, self.__encoder, False),
            self.__write_key)

    def __write(self, value, indent=False, newline=False):
        if indent:
            self.__fd.write(' ' * self.__baseindent * self.__indent)
        self.__fd.write(value)
        if newline:
            self.__fd.write('\n')

    def __write_key(self, key):
        self.__write(self.__encoder.encode(key), indent=self.__indent)
        self.__write(': ')

    def __write_no_comma(self, key, value):
        """Write without a comma."""
        self.__write_key(key)
        self.__write(self.__encoder.encode(value))

        # replace with the comma version, removeing the need for extra if
        # statements.
        self.write = self.__write_comma

    def __write_comma(self, key, value):
        """Write with a comma."""
        if not self.__indent:
            self.__write(', ')
        else:
            self.__write(',', newline=True)
        self.__write_key(key)
        self.__write(self.__encoder.encode(value))

    def close(self):  # pylint: disable=method-hidden
        """Close the Object.

        Once this method is closed calling any of the public methods will
        result in an StreamClosedError being raised.
        """
        if self.__indent:
            self.__write('\n')
        self.__baseindent -= 1
        self.__write('}', indent=True)

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

    def __init__(self, fd, indent, baseindent, encoder, _indent=True):
        self.__fd = fd
        self.__indent = indent
        self.__baseindent = copy.copy(baseindent)
        self.__write('[', indent=_indent, newline=self.__indent)
        self.__baseindent += 1
        self.__encoder = encoder

        self.write = self.__write_no_comma
        self.subobject = functools.partial(
            Open,
            functools.partial(Object, self.__fd, self.__indent,
                              self.__baseindent, self.__encoder))

        self.subarray = functools.partial(
            Open,
            functools.partial(Array, self.__fd, self.__indent,
                              self.__baseindent, self.__encoder))

    def __write(self, value, indent=False, newline=False):
        if indent:
            self.__fd.write(' ' * self.__baseindent * self.__indent)
        self.__fd.write(value)
        if newline:
            self.__fd.write('\n')

    def __write_no_comma(self, value):
        self.__write(self.__encoder.encode(value), indent=self.__indent)
        self.write = self.__write_comma

    def __write_comma(self, value):
        if not self.__indent:
            self.__write(', ')
        else:
            self.__write(',', newline=True)
        self.__write(self.__encoder.encode(value), indent=self.__indent)

    def close(self):  # pylint: disable=method-hidden
        """Close the Object.

        Once this method is closed calling any of the public methods will
        result in an StreamClosedError being raised.
        """
        if self.__indent:
            self.__write('\n')
        self.__baseindent -= 1
        self.__write(']', indent=self.__indent)

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
        assert jtype in ['object', 'array']

        self.filename = filename
        self.__fd = open(filename, 'w')
        self.__inst = self._types[jtype](
            self.__fd, indent, 0, encoder())

        self.subobject = self.__inst.subobject
        self.subarray = self.__inst.subarray
        self.write = self.__inst.write

    def close(self):
        """Close the root element and the file."""
        self.__inst.close()
        self.__fd.close()

    def __enter__(self):
        return self

    def __exit__(self, etype, evalue, traceback):
        self.close()
