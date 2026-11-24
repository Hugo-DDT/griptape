import tempfile
from pathlib import Path

import pytest

from griptape.loaders import JsonLoader


class TestJsonLoader:
    @pytest.fixture(params=["ascii", "utf-8", None])
    def loader(self, request):
        encoding = request.param
        if encoding is None:
            return JsonLoader()
        return JsonLoader(encoding=encoding)

    @pytest.fixture(params=["path_from_resource_path"])
    def create_source(self, request):
        return request.getfixturevalue(request.param)

    def test_load(self, loader, create_source):
        source = create_source("test.json")

        artifact = loader.load(source)

        assert artifact.value["name"] == "John Doe"
        assert artifact.encoding == loader.encoding

    def test_load_collection(self, loader, create_source):
        resource_paths = ["test.json"]
        sources = [create_source(resource_path) for resource_path in resource_paths]

        collection = loader.load_collection(sources)

        keys = {loader.to_key(source) for source in sources}
        assert collection.keys() == keys

        key = next(iter(keys))
        artifact = collection[key]

        assert artifact.encoding == loader.encoding

    def test_load_top_level_json_string_true(self, loader):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.json"
            path.write_bytes(b'"true"')

            artifact = loader.load(str(path))

        assert artifact.value == "true"
        assert isinstance(artifact.value, str)
        assert artifact.encoding == loader.encoding

    def test_load_top_level_json_string_hello(self, loader):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.json"
            path.write_bytes(b'"hello"')

            artifact = loader.load(str(path))

        assert artifact.value == "hello"
        assert isinstance(artifact.value, str)
        assert artifact.encoding == loader.encoding

    def test_load_nested_json_string(self, loader):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.json"
            path.write_bytes(b'{"name":"true"}')

            artifact = loader.load(str(path))

        assert artifact.value["name"] == "true"
        assert isinstance(artifact.value["name"], str)
        assert artifact.encoding == loader.encoding

    @pytest.mark.parametrize(
        ("contents", "expected"),
        [
            (b"true", True),
            (b"false", False),
            (b"null", None),
            (b"123", 123),
            (b"1.5", 1.5),
            (b'[1, "true"]', [1, "true"]),
        ],
    )
    def test_load_other_top_level_json_values(self, loader, contents, expected):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.json"
            path.write_bytes(contents)

            artifact = loader.load(str(path))

        assert artifact.value == expected
        assert type(artifact.value) is type(expected)
        assert artifact.encoding == loader.encoding

    def test_load_top_level_json_string_respects_encoding(self):
        loader = JsonLoader(encoding="latin-1")

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.json"
            path.write_bytes('"café"'.encode("latin-1"))

            artifact = loader.load(str(path))

        assert artifact.value == "café"
        assert isinstance(artifact.value, str)
        assert artifact.encoding == "latin-1"
