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

import copy
import functools
try:
    import simplejson as json
except ImportError:
    import json

__all__ = [
    'Stream',
]


class Open(object):

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

    def __init__(self, fd, indent, baseindent, encoder, _indent=True):
        self.__fd = fd
        self.__indent = indent
        self.__baseindent = copy.copy(baseindent)
        self.__write('{', indent=_indent, newline=self.__indent)
        self.__baseindent += 1
        self.__encoder = encoder

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
        self.__write(self.__encoder.encode(key), indent=True)
        self.__write(': ')

    def __write_no_comma(self, key, value):
        self.__write_key(key)
        self.__write(self.__encoder.encode(value))
        self.write = self.__write_comma

    def __write_comma(self, key, value):
        if not self.__indent:
            self.__write(', ')
        else:
            self.__write(',', newline=True)
        self.__write_key(key)
        self.__write(self.__encoder.encode(value))

    def close(self):
        if self.__indent:
            self.__write('\n')
        self.__baseindent -= 1
        self.__write('}', indent=True)

    def __enter__(self):
        return self

    def __exit__(self, etype, evalue, traceback):
        self.close()


class Array(object):

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

    def close(self):
        if self.__indent:
            self.__write('\n')
        self.__baseindent -= 1
        self.__write(']', indent=True)

    def __enter__(self):
        return self

    def __exit__(self, etype, evalue, traceback):
        self.close()


class Stream(object):

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
        self.__inst.close()
        self.__fd.close()

    def __enter__(self):
        return self

    def __exit__(self, etype, evalue, traceback):
        self.close()
