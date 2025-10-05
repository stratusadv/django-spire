from __future__ import annotations

from django_spire.ai.chat.message_intel import BaseMessageIntel


class ClownFlyingDistanceMessageIntel(BaseMessageIntel):
    _template = 'ai/chat/message/clown_flying_distance_message.html'
    clown_name: str
    distances_in_meters: list[int]

    def content_to_str(self) -> str:
        return f'Clown {self.clown_name} flies {self.distances_in_meters} meters.'


class PirateMessageIntel(BaseMessageIntel):
    _template = 'ai/chat/message/pirate_message.html'
    pirate_ship_name: str
    crew_count: int
    cannon_count: int

    def content_to_str(self) -> str:
        return f'Pirate {self.pirate_ship_name} has {self.crew_count} crew members and {self.cannon_count} cannons.'
