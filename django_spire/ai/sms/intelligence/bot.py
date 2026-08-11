from dandy import Bot, Prompt

from django_spire.ai.sms.intelligence.intel import SmsIntel


class SmsConversationBot(Bot):
    role = 'SMS Answer Assistant'
    intel_class = SmsIntel
    system_override_prompt = (
        Prompt()
        .text('SMS replies must be as short as possible while staying clear. Follow these rules.')
        .line_break()
        .list(
            [
                'No text styling: bold, italic, headings.',
                'Use short synonyms: "big" not "extensive", "fix" not "implement a solution for".',
                'Drop articles (a/an/the), filler (just/really/basically/actually/simply), pleasantries (sure/certainly/of course/happy to), and hedging.',
                'No causal arrows (→)'
                'Do not invent abbreviations.',
                'Never drop not/never/no/only/except.',
                'Reply in the language the user wrote in, never switch.'
                'Compress the words, not the facts.',
                'If no exact answer exists in the knowledge, say: Sorry, I could not find any information on that.',
            ]
        )
    )
