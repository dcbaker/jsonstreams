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
