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

"""Exception classes for jsonstreams."""


class JSONStreamsError(Exception):
    """Base exception for jsonstreams."""


class StreamClosedError(JSONStreamsError):
    """Error raised when writing into a closed Element."""


class ModifyWrongStreamError(JSONStreamsError):
    """This exception is raised when writing to a parent when a child is opened.

    Because of the streaming nature of this module, one cannot write into a
    parent without first closing the child, since there is no way to put the
    data in the parent while the child is opened.

    This Exception should not be caught, it is a fatal exception.
    """


class InvalidTypeError(JSONStreamsError):
    """An exception raised when an invalid type is passed.

    Sometimes a type is invalid for certain purposes. For example, a numeric
    type or null cannot be used as a key in a JSON object.
    """
