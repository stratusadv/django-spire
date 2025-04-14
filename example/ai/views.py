from __future__ import annotations

from typing import Any

from dandy.intel import BaseIntel
from dandy.llm import LlmBot, Prompt
from dandy.recorder import recorder_to_html_file
from django.template.response import TemplateResponse
from typing_extensions import TYPE_CHECKING

from django_spire.ai.decorators import log_ai_interaction_from_recorder

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def ai_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'ai/page/ai_home_page.html'

    horse_intel = None

    if request.method == 'POST':
        class HorseIntel(BaseIntel):
            first_name: str
            breed: str
            description: str
            color: str
            has_cone_taped_to_head: bool

        @log_ai_interaction_from_recorder(request.user)
        def generate_horse_intel(horse_description: Any) -> HorseIntel:
            if not isinstance(horse_description, str):
                raise ValueError('horse_description must be a string')

            return LlmBot.process(
                prompt=horse_description,
                intel_class=HorseIntel,
                postfix_system_prompt=Prompt('Please create a horse based on the users input.')
            )

        if not request.POST.get('legal_user_input'):
            horse_intel = generate_horse_intel(777)
        else:
            horse_intel = generate_horse_intel(request.POST['legal_user_input'])

    return TemplateResponse(request, template, context={
        'horse_intel': horse_intel.model_dump() if horse_intel else None
    })
