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

import pytest

import jsonstreams

_ENCODER = json.JSONEncoder()

# pylint: disable=no-self-use


class TestStream(object):

    @pytest.fixture(autouse=True)
    def chdir(self, tmpdir):
        tmpdir.chdir()

    def test_basic(self):
        s = jsonstreams.Stream('foo', 'object')
        s.write('foo', 'bar')
        s.close()

        with open('foo', 'r') as f:
            assert f.read() == '{"foo": "bar"}'

    def test_context_manager(self):
        with jsonstreams.Stream('foo', 'object') as s:
            s.write('foo', 'bar')

        with open('foo', 'r') as f:
            assert f.read() == '{"foo": "bar"}'

    def test_context_manager_sub(self):
        with jsonstreams.Stream('foo', 'object') as s:
            with s.subarray('foo') as a:
                with a.subarray() as b:
                    with b.subobject() as c:
                        with c.subobject('bar') as _:
                            pass

    def test_sub(self):
        s = jsonstreams.Stream('foo', 'object')
        a = s.subarray('foo')
        b = a.subarray()
        c = b.subobject()
        d = c.subobject('bar')
        d.close()
        c.close()
        b.close()
        a.close()
        s.close()


class TestObject(object):

    @pytest.fixture(autouse=True)
    def chdir(self, tmpdir):
        tmpdir.chdir()

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

        @pytest.mark.parametrize("key,value,expected", [
            ("foo", "bar", '{"foo": "bar"}'),
            ("foo", 1, '{"foo": 1}'),
            ("foo", 1.0, '{"foo": 1.0}'),
            ("foo", None, '{"foo": null}'),
            ("foo", ["bar"], '{"foo": ["bar"]}'),
            (1, "bar", '{1: "bar"}'),
            (1.0, "bar", '{1.0: "bar"}'),
            (None, "bar", '{null: "bar"}'),
            ("foo", {"foo": "bar"}, '{"foo": {"foo": "bar"}}'),
            ("foo", ["foo"], '{"foo": ["foo"]}'),
        ])
        def test_types(self, key, value, expected):
            with open('foo', 'w') as f:
                with jsonstreams.Object(f, 0, 0, _ENCODER) as s:
                    s.write(key, value)

            with open('foo', 'r') as f:
                assert f.read() == expected

    class TestSubobject(object):

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

    class TestSubarray(object):

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

        @pytest.mark.parametrize("value,expected", [
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
