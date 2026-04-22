from __future__ import annotations

from typing import ClassVar

from dandy import Decoder


class IntentDecoder(Decoder):
    mapping_keys_description = 'User Chat Intents'
    mapping: ClassVar = {}
