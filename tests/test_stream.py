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


import json
import textwrap

import pytest # type: ignore
import six
from six.moves import range

import jsonstreams

_ENCODER = json.JSONEncoder()  # type: ignore

# pylint: disable=no-self-use


class TestStream(object):

    @pytest.fixture(autouse=True)
    def chdir(self, tmpdir):
        tmpdir.chdir()

    def test_basic(self):
        s = jsonstreams.Stream(jsonstreams.Type.object, filename='foo')
        s.write('foo', 'bar')
        s.close()

        with open('foo', 'r') as f:
            assert f.read() == '{"foo": "bar"}'

    def test_fd(self):
        with open('foo', 'w') as f:
            with jsonstreams.Stream(jsonstreams.Type.object, fd=f) as s:
                s.write('foo', 'bar')

        with open('foo', 'r') as f:
            assert f.read() == '{"foo": "bar"}'

    def test_context_manager(self):
        with jsonstreams.Stream(jsonstreams.Type.object, filename='foo') as s:
            s.write('foo', 'bar')

        with open('foo', 'r') as f:
            assert f.read() == '{"foo": "bar"}'

    def test_context_manager_sub(self):
        with jsonstreams.Stream(jsonstreams.Type.object, filename='foo') as s:
            with s.subarray('foo') as a:
                with a.subarray() as b:
                    with b.subobject() as c:
                        with c.subobject('bar') as _:
                            pass

    def test_sub(self):
        s = jsonstreams.Stream(jsonstreams.Type.object, filename='foo')
        a = s.subarray('foo')
        b = a.subarray()
        c = b.subobject()
        d = c.subobject('bar')
        d.close()
        c.close()
        b.close()
        a.close()
        s.close()

    def test_write_two(self):
        with jsonstreams.Stream(jsonstreams.Type.object, filename='foo') as s:
            s.write('foo', 'bar')
            s.write('bar', 'foo')

        with open('foo', 'r') as f:
            assert f.read() == '{"foo": "bar", "bar": "foo"}'

    def test_subobject(self):
        with jsonstreams.Stream(jsonstreams.Type.object, filename='foo') as s:
            s.write('foo', 'bar')
            with s.subobject('bar') as b:
                b.write('1', 'foo')

        with open('foo', 'r') as f:
            assert f.read() == '{"foo": "bar", "bar": {"1": "foo"}}'

    def test_subarray(self):
        with jsonstreams.Stream(jsonstreams.Type.array, filename='foo') as s:
            s.write('foo')
            with s.subarray() as b:
                b.write(1)
                b.write(2)

        with open('foo', 'r') as f:
            assert f.read() == '["foo", [1, 2]]'

    def test_encoder_indent(self):
        with jsonstreams.Stream(jsonstreams.Type.object, filename='foo',
                                indent=4) as s:
            s.write('oink', {'bar': {'b': 0}})

        with open('foo', 'r') as f:
            actual = f.read()

        assert actual == textwrap.dedent("""\
            {
                "oink": {
                "bar": {
                    "b": 0
                }
            }
            }""")

    def test_pretty(self):
        with jsonstreams.Stream(jsonstreams.Type.array, filename='foo',
                                indent=4, pretty=True) as s:
            s.write({'bar': {"b": 0}})
            s.write({'fob': {"f": 0}})

        with open('foo', 'r') as f:
            actual = f.read()

        assert actual == textwrap.dedent("""\
            [
                {
                    "bar": {
                        "b": 0
                    }
                },
                {
                    "fob": {
                        "f": 0
                    }
                }
            ]""")

    class TestIterWrite(object):
        """Tests for the iterwrite object."""

        class TestArray(object):
            """Tests for array object."""

            @pytest.fixture(autouse=True)
            def chdir(self, tmpdir):
                tmpdir.chdir()

            def test_basic(self):
                with jsonstreams.Stream(
                        jsonstreams.Type.array, filename='foo') as s:
                    s.iterwrite(range(5))

                with open('foo', 'r') as f:
                    actual = json.load(f)

                assert actual == list(range(5))

            def test_mixed(self):
                with jsonstreams.Stream(
                        jsonstreams.Type.array, filename='foo') as s:
                    s.iterwrite(range(5))
                    s.write('a')

                with open('foo', 'r') as f:
                    actual = json.load(f)

                assert actual == list(range(5)) + ['a']

        class TestObject(object):
            """Tests for array object."""

            @pytest.fixture(autouse=True)
            def chdir(self, tmpdir):
                tmpdir.chdir()

            def test_basic(self):
                with jsonstreams.Stream(
                        jsonstreams.Type.object, filename='foo') as s:
                    s.iterwrite(
                        ((str(s), k) for s in range(5) for k in range(5)))

                with open('foo', 'r') as f:
                    actual = json.load(f)

                assert actual == {str(s): k for s in range(5) for k in range(5)}

            def test_mixed(self):
                with jsonstreams.Stream(
                        jsonstreams.Type.object, filename='foo') as s:
                    s.iterwrite(
                        ((str(s), k) for s in range(5) for k in range(5)))
                    s.write("6", 'a')

                with open('foo', 'r') as f:
                    actual = json.load(f)

                expected = {str(s): k for s in range(5) for k in range(5)}
                expected['6'] = 'a'

                assert actual == expected


class TestObject(object):

    def test_init(self):
        with open('foo', 'w') as f:
            jsonstreams.Object(f, 0, 0, _ENCODER)

        with open('foo', 'r') as f:
            assert f.read() == '{'

    def test_context_manager(self):
        with open('foo', 'w') as f:
            with jsonstreams.Object(f, 0, 0, _ENCODER) as _:
                pass

        with open('foo', 'r') as f:
            assert f.read() == '{}'

    class TestWrite(object):

        @pytest.fixture(autouse=True)
        def chdir(self, tmpdir):
            tmpdir.chdir()

        class TestWithoutIndent(object):

            @pytest.fixture(autouse=True)
            def chdir(self, tmpdir):
                tmpdir.chdir()

            def test_write_one(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                        s.write('foo', 'bar')

                with open('foo', 'r') as f:
                    assert f.read() == '{"foo": "bar"}'

            def test_write_two(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                        s.write('foo', 'bar')
                        s.write('bar', 'foo')

                with open('foo', 'r') as f:
                    assert f.read() == '{"foo": "bar", "bar": "foo"}'

            def test_complex(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                        s.write('foo', {"1": 'bar'})

                with open('foo', 'r') as f:
                    assert f.read() == '{"foo": {"1": "bar"}}'

        class TestWithIndent(object):

            @pytest.fixture(autouse=True)
            def chdir(self, tmpdir):
                tmpdir.chdir()

            def test_write_one(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Object(f, 4, 0, _ENCODER) as s:
                        s.write('foo', 'bar')

                with open('foo', 'r') as f:
                    assert f.read() == textwrap.dedent("""\
                        {
                            "foo": "bar"
                        }""")

            def test_write_two(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Object(f, 4, 0, _ENCODER) as s:
                        s.write('foo', 'bar')
                        s.write('bar', 'foo')

                with open('foo', 'r') as f:
                    assert f.read() == textwrap.dedent("""\
                        {
                            "foo": "bar",
                            "bar": "foo"
                        }""")

            def test_complex(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Object(f, 4, 0, _ENCODER) as s:
                        s.write('foo', {"1": 'bar'})

                with open('foo', 'r') as f:
                    assert f.read() == textwrap.dedent("""\
                        {
                            "foo": {"1": "bar"}
                        }""")

        @pytest.mark.parametrize("key,value,expected", [  # type: ignore
            ("foo", "bar", '{"foo": "bar"}'),
            ("foo", 1, '{"foo": 1}'),
            ("foo", 1.0, '{"foo": 1.0}'),
            ("foo", None, '{"foo": null}'),
            ("foo", ["bar"], '{"foo": ["bar"]}'),
            ("foo", {"foo": "bar"}, '{"foo": {"foo": "bar"}}'),
            ("foo", ["foo"], '{"foo": ["foo"]}'),
        ])
        def test_types(self, key, value, expected):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                    s.write(key, value)

            with open('foo', 'r') as f:
                assert f.read() == expected

        @pytest.mark.parametrize("key", [1, 1.0, None])
        def test_invalid_key_types(self, key):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                    with pytest.raises(jsonstreams.InvalidTypeError):
                        s.write(key, 'foo')

        def test_pretty(self):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 4, 0, json.JSONEncoder(indent=4),
                                        pretty=True) as s:
                    s.write("1", {'bar': {"b": 0}})
                    s.write("2", {'fob': {"f": 0}})

            with open('foo', 'r') as f:
                actual = f.read()

            assert actual == textwrap.dedent("""\
                {
                    "1": {
                        "bar": {
                            "b": 0
                        }
                    },
                    "2": {
                        "fob": {
                            "f": 0
                        }
                    }
                }""")

    class TestSubobject(object):
        """Tests for the suboboject method."""

        @pytest.fixture(autouse=True)
        def chdir(self, tmpdir):
            tmpdir.chdir()

        def test_basic(self):
            with open('foo', 'w') as f:
                s = jsonstreams.Object(f, 0, 0, _ENCODER)
                p = s.subobject('ook')
                p.write('foo', 'bar')
                p.close()
                s.close()

            with open('foo', 'r') as f:
                assert f.read() == '{"ook": {"foo": "bar"}}'

        def test_context_manager(self):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                    with s.subobject('ook') as p:
                        p.write('foo', 'bar')

            with open('foo', 'r') as f:
                assert f.read() == '{"ook": {"foo": "bar"}}'

        def test_indent(self):
            with open('foo', 'w') as f:
                s = jsonstreams.Object(f, 4, 0, _ENCODER)
                p = s.subobject('ook')
                p.write('foo', 'bar')
                p.close()
                s.close()

            with open('foo', 'r') as f:
                assert f.read() == textwrap.dedent("""\
                    {
                        "ook": {
                            "foo": "bar"
                        }
                    }""")

        def test_context_manager_indent(self):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 4, 0, _ENCODER) as s:
                    with s.subobject('ook') as p:
                        p.write('foo', 'bar')

            with open('foo', 'r') as f:
                assert f.read() == textwrap.dedent("""\
                    {
                        "ook": {
                            "foo": "bar"
                        }
                    }""")

        class TestNestedContextManager(object):
            """Test various nested configurations with context managers."""

            def test_inner(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                        with s.subobject('ook') as p:
                            p.write('foo', 'bar')
                            p.write("1", 'bar')

                with open('foo', 'r') as f:
                    assert f.read() == '{"ook": {"foo": "bar", "1": "bar"}}'

            def test_outer_inner(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                        s.write('foo', 'bar')
                        with s.subobject('ook') as p:
                            p.write("1", 'bar')

                with open('foo', 'r') as f:
                    assert f.read() == '{"foo": "bar", "ook": {"1": "bar"}}'

            def test_inner_outer(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                        with s.subobject('ook') as p:
                            p.write("1", 'bar')
                        s.write('foo', 'bar')

                with open('foo', 'r') as f:
                    assert f.read() == '{"ook": {"1": "bar"}, "foo": "bar"}'

            def test_outer_inner_outer(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                        s.write("1", 'bar')
                        with s.subobject('ook') as p:
                            p.write("1", 'bar')
                        s.write('foo', 'bar')

                with open('foo', 'r') as f:
                    assert f.read() == \
                        '{"1": "bar", "ook": {"1": "bar"}, "foo": "bar"}'

        class TestNested(object):
            """Test various nested configurations."""

            def test_inner(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Object(f, 0, 0, _ENCODER)
                    p = s.subobject("2")
                    p.write("1", 'bar')
                    p.close()
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == '{"2": {"1": "bar"}}'

            def test_outer_inner(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Object(f, 0, 0, _ENCODER)
                    s.write("1", 'foo')
                    p = s.subobject("2")
                    p.write("1", 'bar')
                    p.close()
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == '{"1": "foo", "2": {"1": "bar"}}'

            def test_inner_outer(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Object(f, 0, 0, _ENCODER)
                    p = s.subobject("2")
                    p.write("1", 'bar')
                    p.close()
                    s.write("1", 'foo')
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == '{"2": {"1": "bar"}, "1": "foo"}'

            def test_outer_inner_outer(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Object(f, 0, 0, _ENCODER)
                    s.write('1', 'foo')
                    p = s.subobject('2')
                    p.write('1', 'bar')
                    p.close()
                    s.write('3', 'foo')
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == \
                        '{"1": "foo", "2": {"1": "bar"}, "3": "foo"}'

    class TestSubarray(object):
        """Tests for the subarray method."""

        @pytest.fixture(autouse=True)
        def chdir(self, tmpdir):
            tmpdir.chdir()

        def test_basic(self):
            with open('foo', 'w') as f:
                s = jsonstreams.Object(f, 0, 0, _ENCODER)
                p = s.subarray('ook')
                p.write('foo')
                p.close()
                s.close()

            with open('foo', 'r') as f:
                assert f.read() == '{"ook": ["foo"]}'

        def test_context_manager(self):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                    with s.subarray('ook') as p:
                        p.write('foo')

            with open('foo', 'r') as f:
                assert f.read() == '{"ook": ["foo"]}'

        def test_indent(self):
            with open('foo', 'w') as f:
                s = jsonstreams.Object(f, 4, 0, _ENCODER)
                p = s.subarray('ook')
                p.write('foo')
                p.close()
                s.close()

            with open('foo', 'r') as f:
                assert f.read() == textwrap.dedent("""\
                    {
                        "ook": [
                            "foo"
                        ]
                    }""")

        def test_context_manager_indent(self):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 4, 0, _ENCODER) as s:
                    with s.subarray('ook') as p:
                        p.write('foo')

            with open('foo', 'r') as f:
                assert f.read() == textwrap.dedent("""\
                    {
                        "ook": [
                            "foo"
                        ]
                    }""")

        class TestNestedContextManager(object):
            """Test various nested configurations with context managers."""

            def test_inner(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                        with s.subarray('ook') as p:
                            p.write('foo')
                            p.write(1)

                with open('foo', 'r') as f:
                    assert f.read() == '{"ook": ["foo", 1]}'

            def test_outer_inner(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                        s.write('foo', 'bar')
                        with s.subarray('ook') as p:
                            p.write(1)

                with open('foo', 'r') as f:
                    assert f.read() == '{"foo": "bar", "ook": [1]}'

            def test_inner_outer(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                        with s.subarray('ook') as p:
                            p.write(1)
                        s.write('foo', 'bar')

                with open('foo', 'r') as f:
                    assert f.read() == '{"ook": [1], "foo": "bar"}'

            def test_outer_inner_outer(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                        s.write("1", 'bar')
                        with s.subarray('ook') as p:
                            p.write(1)
                        s.write('foo', 'bar')

                with open('foo', 'r') as f:
                    assert f.read() == \
                        '{"1": "bar", "ook": [1], "foo": "bar"}'

        class TestNested(object):
            """Test various nested configurations."""

            def test_inner(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Object(f, 0, 0, _ENCODER)
                    p = s.subarray("2")
                    p.write(1)
                    p.close()
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == '{"2": [1]}'

            def test_outer_inner(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Object(f, 0, 0, _ENCODER)
                    s.write("1", 'foo')
                    p = s.subarray("2")
                    p.write(1)
                    p.close()
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == '{"1": "foo", "2": [1]}'

            def test_inner_outer(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Object(f, 0, 0, _ENCODER)
                    p = s.subarray("2")
                    p.write(1)
                    p.close()
                    s.write("1", 'foo')
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == '{"2": [1], "1": "foo"}'

            def test_outer_inner_outer(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Object(f, 0, 0, _ENCODER)
                    s.write('1', 'foo')
                    p = s.subarray('2')
                    p.write(1)
                    p.close()
                    s.write('3', 'foo')
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == '{"1": "foo", "2": [1], "3": "foo"}'

    class TestClose(object):

        @pytest.fixture(autouse=True)
        def chdir(self, tmpdir):
            tmpdir.chdir()

        def test_basic(self):
            with open('foo', 'w') as f:
                test = jsonstreams.Object(f, 0, 0, _ENCODER)
                test.close()

            with open('foo', 'r') as f:
                assert f.read() == '{}'

        def test_close(self):
            with open('foo', 'w') as f:
                test = jsonstreams.Object(f, 0, 0, _ENCODER)
                test.close()

                with pytest.raises(jsonstreams.StreamClosedError):
                    test.write('foo', 'bar')

        def test_write(self):
            with open('foo', 'w') as f:
                test = jsonstreams.Object(f, 0, 0, _ENCODER)
                test.close()

                with pytest.raises(jsonstreams.StreamClosedError):
                    test.close()

        def test_subarray(self):
            with open('foo', 'w') as f:
                test = jsonstreams.Object(f, 0, 0, _ENCODER)
                test.close()

                with pytest.raises(jsonstreams.StreamClosedError):
                    test.subarray('foo')

        def test_subobject(self):
            with open('foo', 'w') as f:
                test = jsonstreams.Object(f, 0, 0, _ENCODER)
                test.close()

                with pytest.raises(jsonstreams.StreamClosedError):
                    test.subobject('foo')

    class TestWriteToParent(object):
        """Tests for writing to the parent with a subobject open."""

        @pytest.fixture(autouse=True)
        def chdir(self, tmpdir):
            tmpdir.chdir()

        def test_subobject(self):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 0, 0, _ENCODER) as a:
                    with a.subobject('foo') as b:
                        with pytest.raises(jsonstreams.ModifyWrongStreamError):
                            a.write('foo', 'bar')

        def test_subarray(self):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 0, 0, _ENCODER) as a:
                    with a.subarray('foo') as b:
                        with pytest.raises(jsonstreams.ModifyWrongStreamError):
                            a.write('foo', 'bar')

    class TestIterWrite(object):
        """Tests for the iterwrite object."""

        @pytest.fixture(autouse=True)
        def chdir(self, tmpdir):
            tmpdir.chdir()

        def test_basic(self):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 0, 0, _ENCODER) as a:
                    a.iterwrite(six.iteritems({'a': 1, '2': 2, 'foo': None}))

            with open('foo', 'r') as f:
                actual = json.load(f)

            assert actual == {"a": 1, "2": 2, "foo": None}

        def test_mixed(self):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 0, 0, _ENCODER) as a:
                    a.iterwrite(six.iteritems({'a': 1, '2': 2, 'foo': None}))
                    a.write('bar', 3)

            with open('foo', 'r') as f:
                actual = json.load(f)

            assert actual == {"a": 1, "2": 2, "foo": None, "bar": 3}

        def test_pretty_multiple(self):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 4, 0, _ENCODER, pretty=True) as a:
                    a.iterwrite((str(i), i) for i in range(5))

            with open('foo', 'r') as f:
                actual = json.load(f)

            assert actual == {str(i): i for i in range(5)}

        def test_pretty_one(self):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 4, 0, _ENCODER, pretty=True) as a:
                    a.iterwrite((str(i), i) for i in range(1))

            with open('foo', 'r') as f:
                actual = json.load(f)

            assert actual == {str(i): i for i in range(1)}

            with open('foo', 'r') as f:
                actual = f.read()

            assert actual == textwrap.dedent("""\
                {
                    "0": 0
                }""")

        def test_pretty_subobject(self):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 4, 0, _ENCODER, pretty=True) as a:
                    a.iterwrite((str(i), i) for i in range(5))
                    with a.subobject('foo') as b:
                        b.iterwrite((str(i), i) for i in range(2))

            expected = {str(i): i for i in range(5)}
            expected['foo'] = {str(i): i for i in range(2)}

            with open('foo', 'r') as f:
                actual = json.load(f)

            assert actual == expected

        def test_pretty_subarray(self):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 4, 0, _ENCODER, pretty=True) as a:
                    a.iterwrite((str(i), i) for i in range(5))
                    with a.subarray('foo') as b:
                        b.iterwrite(range(2))

            expected = {str(i): i for i in range(5)}
            expected['foo'] = list(range(2))

            with open('foo', 'r') as f:
                actual = json.load(f)

            assert actual == expected


class TestArray(object):

    @pytest.fixture(autouse=True)
    def chdir(self, tmpdir):
        tmpdir.chdir()

    def test_init(self):
        with open('foo', 'w') as f:
            jsonstreams.Array(f, 0, 0, _ENCODER)

        with open('foo', 'r') as f:
            assert f.read() == '['

    def test_context_manager(self):
        with open('foo', 'w') as f:
            with jsonstreams.Array(f, 0, 0, _ENCODER) as _:
                pass

        with open('foo', 'r') as f:
            assert f.read() == '[]'

    class TestWrite(object):

        @pytest.fixture(autouse=True)
        def chdir(self, tmpdir):
            tmpdir.chdir()

        class TestWithoutIndent(object):

            @pytest.fixture(autouse=True)
            def chdir(self, tmpdir):
                tmpdir.chdir()

            def test_write_one(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Array(f, 0, 0, _ENCODER) as s:
                        s.write('foo')

                with open('foo', 'r') as f:
                    assert f.read() == '["foo"]'

            def test_write_two(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Array(f, 0, 0, _ENCODER) as s:
                        s.write('foo')
                        s.write('bar')

                with open('foo', 'r') as f:
                    assert f.read() == '["foo", "bar"]'

            def test_complex(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Array(f, 0, 0, _ENCODER) as s:
                        s.write({"1": 'bar'})

                with open('foo', 'r') as f:
                    assert f.read() == '[{"1": "bar"}]'

        class TestWithIndent(object):

            @pytest.fixture(autouse=True)
            def chdir(self, tmpdir):
                tmpdir.chdir()

            def test_write_one(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Array(f, 4, 0, _ENCODER) as s:
                        s.write('foo')

                with open('foo', 'r') as f:
                    assert f.read() == textwrap.dedent("""\
                        [
                            "foo"
                        ]""")

            def test_write_two(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Array(f, 4, 0, _ENCODER) as s:
                        s.write('foo')
                        s.write('bar')

                with open('foo', 'r') as f:
                    assert f.read() == textwrap.dedent("""\
                        [
                            "foo",
                            "bar"
                        ]""")

            def test_complex(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Array(f, 4, 0, _ENCODER) as s:
                        s.write({"1": 'bar'})

                with open('foo', 'r') as f:
                    assert f.read() == textwrap.dedent("""\
                        [
                            {"1": "bar"}
                        ]""")

        @pytest.mark.parametrize("value,expected", [  # type: ignore
            ("foo", '["foo"]'),
            (1, '[1]'),
            (1.0, '[1.0]'),
            (None, '[null]'),
            ({"foo": "bar"}, '[{"foo": "bar"}]'),
            (["foo"], '[["foo"]]'),
        ])
        def test_types(self, value, expected):
            with open('foo', 'w') as f:
                with jsonstreams.Array(f, 0, 0, _ENCODER) as s:
                    s.write(value)

            with open('foo', 'r') as f:
                assert f.read() == expected

        def test_pretty(self):
            with open('foo', 'w') as f:
                with jsonstreams.Array(f, 4, 0, json.JSONEncoder(indent=4),
                                       pretty=True) as s:
                    s.write({'bar': {"b": 0}})
                    s.write({'fob': {"f": 0}})

            with open('foo', 'r') as f:
                actual = f.read()

            assert actual == textwrap.dedent("""\
                [
                    {
                        "bar": {
                            "b": 0
                        }
                    },
                    {
                        "fob": {
                            "f": 0
                        }
                    }
                ]""")

    class TestSubobject(object):

        @pytest.fixture(autouse=True)
        def chdir(self, tmpdir):
            tmpdir.chdir()

        def test_basic(self):
            with open('foo', 'w') as f:
                s = jsonstreams.Array(f, 0, 0, _ENCODER)
                p = s.subobject()
                p.write('foo', 'bar')
                p.close()
                s.close()

            with open('foo', 'r') as f:
                assert f.read() == '[{"foo": "bar"}]'

        def test_context_manager(self):
            with open('foo', 'w') as f:
                with jsonstreams.Array(f, 0, 0, _ENCODER) as s:
                    with s.subobject() as p:
                        p.write('foo', 'bar')

            with open('foo', 'r') as f:
                assert f.read() == '[{"foo": "bar"}]'

        def test_indent(self):
            with open('foo', 'w') as f:
                s = jsonstreams.Array(f, 4, 0, _ENCODER)
                p = s.subobject()
                p.write('foo', 'bar')
                p.close()
                s.close()

            with open('foo', 'r') as f:
                assert f.read() == textwrap.dedent("""\
                    [
                        {
                            "foo": "bar"
                        }
                    ]""")

        def test_context_manager_indent(self):
            with open('foo', 'w') as f:
                with jsonstreams.Array(f, 4, 0, _ENCODER) as s:
                    with s.subobject() as p:
                        p.write('foo', 'bar')

            with open('foo', 'r') as f:
                assert f.read() == textwrap.dedent("""\
                    [
                        {
                            "foo": "bar"
                        }
                    ]""")

        class TestNestedContextManager(object):
            """Test various nested configurations with context managers."""

            def test_inner(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Array(f, 0, 0, _ENCODER) as s:
                        with s.subobject() as p:
                            p.write('foo', 'bar')
                            p.write("1", 'bar')

                with open('foo', 'r') as f:
                    assert f.read() == '[{"foo": "bar", "1": "bar"}]'

            def test_outer_inner(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Array(f, 0, 0, _ENCODER) as s:
                        s.write('foo')
                        with s.subobject() as p:
                            p.write("1", 'bar')

                with open('foo', 'r') as f:
                    assert f.read() == '["foo", {"1": "bar"}]'

            def test_inner_outer(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Array(f, 0, 0, _ENCODER) as s:
                        with s.subobject() as p:
                            p.write("1", 'bar')
                        s.write('foo')

                with open('foo', 'r') as f:
                    assert f.read() == '[{"1": "bar"}, "foo"]'

            def test_outer_inner_outer(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Array(f, 0, 0, _ENCODER) as s:
                        s.write(1)
                        with s.subobject() as p:
                            p.write("1", 'bar')
                        s.write(2)

                with open('foo', 'r') as f:
                    assert f.read() == '[1, {"1": "bar"}, 2]'

        class TestNested(object):
            """Test various nested configurations."""

            def test_inner(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Array(f, 0, 0, _ENCODER)
                    p = s.subobject()
                    p.write('foo', 'bar')
                    p.write('1', 'bar')
                    p.close()
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == '[{"foo": "bar", "1": "bar"}]'

            def test_outer_inner(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Array(f, 0, 0, _ENCODER)
                    s.write('foo')
                    p = s.subobject()
                    p.write('1', 'bar')
                    p.close()
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == '["foo", {"1": "bar"}]'

            def test_inner_outer(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Array(f, 0, 0, _ENCODER)
                    p = s.subobject()
                    p.write('1', 'bar')
                    p.close()
                    s.write('foo')
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == '[{"1": "bar"}, "foo"]'

            def test_outer_inner_outer(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Array(f, 0, 0, _ENCODER)
                    s.write(1)
                    p = s.subobject()
                    p.write('1', 'bar')
                    p.close()
                    s.write(2)
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == '[1, {"1": "bar"}, 2]'

    class TestSubarray(object):

        @pytest.fixture(autouse=True)
        def chdir(self, tmpdir):
            tmpdir.chdir()

        def test_basic(self):
            with open('foo', 'w') as f:
                s = jsonstreams.Array(f, 0, 0, _ENCODER)
                p = s.subarray()
                p.write('foo')
                p.close()
                s.close()

            with open('foo', 'r') as f:
                assert f.read() == '[["foo"]]'

        def test_context_manager(self):
            with open('foo', 'w') as f:
                with jsonstreams.Array(f, 0, 0, _ENCODER) as s:
                    with s.subarray() as p:
                        p.write('foo')

            with open('foo', 'r') as f:
                assert f.read() == '[["foo"]]'

        def test_indent(self):
            with open('foo', 'w') as f:
                s = jsonstreams.Array(f, 4, 0, _ENCODER)
                p = s.subarray()
                p.write('foo')
                p.close()
                s.close()

            with open('foo', 'r') as f:
                assert f.read() == textwrap.dedent("""\
                    [
                        [
                            "foo"
                        ]
                    ]""")

        def test_context_manager_indent(self):
            with open('foo', 'w') as f:
                with jsonstreams.Array(f, 4, 0, _ENCODER) as s:
                    with s.subarray() as p:
                        p.write('foo')

            with open('foo', 'r') as f:
                assert f.read() == textwrap.dedent("""\
                    [
                        [
                            "foo"
                        ]
                    ]""")

        class TestNestedContextManager(object):
            """Test various nested configurations with context managers."""

            def test_inner(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Array(f, 0, 0, _ENCODER) as s:
                        with s.subarray() as p:
                            p.write('foo')
                            p.write('bar')

                with open('foo', 'r') as f:
                    assert f.read() == '[["foo", "bar"]]'

            def test_outer_inner(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Array(f, 0, 0, _ENCODER) as s:
                        s.write('foo')
                        with s.subarray() as p:
                            p.write('bar')

                with open('foo', 'r') as f:
                    assert f.read() == '["foo", ["bar"]]'

            def test_inner_outer(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Array(f, 0, 0, _ENCODER) as s:
                        with s.subarray() as p:
                            p.write('bar')
                        s.write('foo')

                with open('foo', 'r') as f:
                    assert f.read() == '[["bar"], "foo"]'

            def test_outer_inner_outer(self):
                with open('foo', 'w') as f:
                    with jsonstreams.Array(f, 0, 0, _ENCODER) as s:
                        s.write(1)
                        with s.subarray() as p:
                            p.write('bar')
                        s.write(2)

                with open('foo', 'r') as f:
                    assert f.read() == '[1, ["bar"], 2]'

        class TestNested(object):
            """Test various nested configurations."""

            def test_inner(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Array(f, 0, 0, _ENCODER)
                    p = s.subarray()
                    p.write('foo')
                    p.write('bar')
                    p.close()
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == '[["foo", "bar"]]'

            def test_outer_inner(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Array(f, 0, 0, _ENCODER)
                    s.write('foo')
                    p = s.subarray()
                    p.write('bar')
                    p.close()
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == '["foo", ["bar"]]'

            def test_inner_outer(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Array(f, 0, 0, _ENCODER)
                    p = s.subarray()
                    p.write('foo')
                    p.close()
                    s.write('bar')
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == '[["foo"], "bar"]'

            def test_outer_inner_outer(self):
                with open('foo', 'w') as f:
                    s = jsonstreams.Array(f, 0, 0, _ENCODER)
                    s.write(1)
                    p = s.subarray()
                    p.write(1)
                    p.close()
                    s.write(2)
                    s.close()

                with open('foo', 'r') as f:
                    assert f.read() == '[1, [1], 2]'

    class TestClose(object):

        @pytest.fixture(autouse=True)
        def chdir(self, tmpdir):
            tmpdir.chdir()

        def test_basic(self):
            with open('foo', 'w') as f:
                test = jsonstreams.Array(f, 0, 0, _ENCODER)
                test.close()

            with open('foo', 'r') as f:
                assert f.read() == '[]'

        def test_close(self):
            with open('foo', 'w') as f:
                test = jsonstreams.Array(f, 0, 0, _ENCODER)
                test.close()

                with pytest.raises(jsonstreams.StreamClosedError):
                    test.write('foo')

        def test_write(self):
            with open('foo', 'w') as f:
                test = jsonstreams.Array(f, 0, 0, _ENCODER)
                test.close()

                with pytest.raises(jsonstreams.StreamClosedError):
                    test.close()

        def test_subarray(self):
            with open('foo', 'w') as f:
                test = jsonstreams.Array(f, 0, 0, _ENCODER)
                test.close()

                with pytest.raises(jsonstreams.StreamClosedError):
                    test.subarray()

        def test_subobject(self):
            with open('foo', 'w') as f:
                test = jsonstreams.Array(f, 0, 0, _ENCODER)
                test.close()

                with pytest.raises(jsonstreams.StreamClosedError):
                    test.subobject()

    class TestWriteToParent(object):
        """Tests for writing to the parent with a subobject open."""

        @pytest.fixture(autouse=True)
        def chdir(self, tmpdir):
            tmpdir.chdir()

        def test_subobject(self):
            with open('foo', 'w') as f:
                with jsonstreams.Array(f, 0, 0, _ENCODER) as a:
                    with a.subobject() as b:
                        with pytest.raises(jsonstreams.ModifyWrongStreamError):
                            a.write('foo')

        def test_subarray(self):
            with open('foo', 'w') as f:
                with jsonstreams.Array(f, 0, 0, _ENCODER) as a:
                    with a.subarray() as b:
                        with pytest.raises(jsonstreams.ModifyWrongStreamError):
                            a.write('foo')

    class TestIterWrite(object):
        """Tests for the iterwrite object."""

        @pytest.fixture(autouse=True)
        def chdir(self, tmpdir):
            tmpdir.chdir()

        def test_basic(self):
            with open('foo', 'w') as f:
                with jsonstreams.Array(f, 0, 0, _ENCODER) as a:
                    a.iterwrite(range(5))

            with open('foo', 'r') as f:
                actual = json.load(f)

            assert actual == list(range(5))

        def test_mixed(self):
            with open('foo', 'w') as f:
                with jsonstreams.Array(f, 0, 0, _ENCODER) as a:
                    a.iterwrite(range(5))
                    a.write('a')

            with open('foo', 'r') as f:
                actual = json.load(f)

            assert actual == list(range(5)) + ['a']

        def test_pretty_multiple(self):
            with open('foo', 'w') as f:
                with jsonstreams.Array(f, 4, 0, _ENCODER, pretty=True) as a:
                    a.iterwrite(range(5))

            with open('foo', 'r') as f:
                actual = json.load(f)

            assert actual == list(range(5))

            with open('foo', 'r') as f:
                actual = f.read()

            assert actual == textwrap.dedent("""\
                [
                    0,
                    1,
                    2,
                    3,
                    4
                ]""")

        def test_pretty_one(self):
            with open('foo', 'w') as f:
                with jsonstreams.Array(f, 4, 0, _ENCODER, pretty=True) as a:
                    a.iterwrite(range(1))

            with open('foo', 'r') as f:
                actual = json.load(f)

            assert actual == list(range(1))

            with open('foo', 'r') as f:
                actual = f.read()

            assert actual == textwrap.dedent("""\
                [
                    0
                ]""")

        def test_pretty_subobject(self):
            with open('foo', 'w') as f:
                with jsonstreams.Array(f, 4, 0, _ENCODER, pretty=True) as a:
                    a.iterwrite(range(5))
                    with a.subobject() as b:
                        b.iterwrite((str(i), i) for i in range(2))

            expected = list(range(5))
            expected.append({str(i): i for i in range(2)})

            with open('foo', 'r') as f:
                actual = json.load(f)

            assert actual == expected

        def test_pretty_subarray(self):
            with open('foo', 'w') as f:
                with jsonstreams.Array(f, 4, 0, _ENCODER, pretty=True) as a:
                    a.iterwrite(range(5))
                    with a.subarray() as b:
                        b.iterwrite(range(2))

            expected = list(range(5))
            expected.append(list(range(2)))

            with open('foo', 'r') as f:
                actual = json.load(f)

            assert actual == expected
