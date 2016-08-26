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

>>> with Stream('array', filename='foo') as s:
...     s.write('foo')
...     s.write('bar')

Each element can also open a subelement, either via the subarray() or
subobject() method.

>>> with Stream('array', filename='foo') as s:
...     s.write('foo')
...     with s.subobject() as o:
...         o.write('1', 'bar')

Any object that can be serialized can be passed (although passing some elements
as object keys is not supported, and should not be passed).

>>> with Stream('object', filename='foo') as s:
...     s.write('foo', {'foo': 'bar'})

It is very important to note that while the Array and Object classes present
the same API, the signature of their write and iterwrite methods are
necessarily different. For write, Array accepts a single element, for Object it
requires two elements, the key and the value. With iteritems Array accepts a
an iterable returning a single valid item, while Object accepts an iterable
returning a (key, value) tuple pair.

>>> with Stream('object', filename='foo') as s:
...     s.iterwrite(((str(k), k) for k in range(5)))
...     with s.subarray('foo') as a:
...         a.iterwrite(range(5))
"""

from .exceptions import *  # pylint: disable=wildcard-import

try:
    from ._cython import Stream
except ImportError:
    from ._python import Stream

__version__ = '0.3.2'
