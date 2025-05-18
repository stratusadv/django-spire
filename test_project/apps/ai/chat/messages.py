from django_spire.ai.chat.messages import BaseMessageIntel


class ClownFlyingDistanceMessageIntel(BaseMessageIntel):
    _template = 'ai/chat/message/clown_flying_distance_message.html'
    clown_name: str
    distances_in_meters: list[int]

    def content_to_str(self) -> str:
        return f'Clown {self.clown_name} flies {self.distances_in_meters} meters.'