from __future__ import annotations

import json

from attrs import define

from griptape.artifacts import JsonArtifact
from griptape.loaders import BaseFileLoader


@define
class JsonLoader(BaseFileLoader[JsonArtifact]):
    def parse(self, data: bytes) -> JsonArtifact:
        # JsonArtifact treats a str as JSON text and decodes it again. The file
        # bytes are already parsed here, so hand the value back as JSON text.
        parsed = json.loads(data.decode(self.encoding))
        return JsonArtifact(json.dumps(parsed), encoding=self.encoding)
