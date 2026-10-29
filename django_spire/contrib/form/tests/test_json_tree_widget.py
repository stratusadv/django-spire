from __future__ import annotations

import json
from html import unescape

from django.test import SimpleTestCase

from django_spire.celery import models
from django_spire.celery.admin import CeleryTaskModelForm
from django_spire.contrib.form.widgets import JsonTreeWidget

STORYBOOK_META = {
    'data': {
        'cover': {'image_prompt': 'A vibrant storybook watercolor illustration of a retro taco truck.'},
        'pages': [
            {
                'panels': [
                    {
                        'caption': 'The sun hangs low over the endless dunes.',
                        'dialogue': '',
                        'characters': [],
                        'image_prompt': 'Low sun over endless dunes.',
                        'panel_number': 1,
                    },
                    {
                        'caption': 'Mateo Vargas watches the horizon.',
                        'dialogue': '"You\'re late. But you\'re here."',
                        'characters': ['Mateo Vargas', 'Elena Cruz'],
                        'image_prompt': 'Interior of faded truck.',
                        'panel_number': 2,
                    },
                ],
                'columns': 2,
                'page_number': 1,
            }
        ],
        'title': 'The Last Taco in the Wasteland',
        'synopsis': 'In a sun-bleached desert, a lonely taco truck holds the last secret recipe.',
        'characters': {
            'items': [
                {
                    'age': 65,
                    'role': 'Protagonist',
                    'gender': 'Male',
                    'last_name': 'Vargas',
                    'first_name': 'Mateo',
                    'description': 'The weary owner of El Solitario.',
                    'appearance_prompt': 'A weathered 65-year-old man.',
                },
                {
                    'age': 28,
                    'role': 'Deuteragonist',
                    'gender': 'Female',
                    'last_name': 'Cruz',
                    'first_name': 'Elena',
                    'description': 'A determined young traveler.',
                    'appearance_prompt': 'A determined 28-year-old woman.',
                },
            ]
        },
        'worker_hostname': 'celery@brian-laptop',
    },
    'error': None,
    'retries': 0,
    'progress': 1.0,
    'failed_time': None,
    'started_time': 1793243207.0686362,
    'completed_time': 1793243255.7635705,
    'error_traceback': None,
    'last_update_time': 1793243255.7635612,
    'estimated_completed_time': 1793243257.4872863,
}


class TestJsonTreeWidget(SimpleTestCase):
    def test_render_dict_with_items_key(self) -> None:
        widget = JsonTreeWidget()
        value = {'characters': {'items': [{'age': 65, 'role': 'Protagonist'}]}}

        html = widget.render('_task_meta', json.dumps(value), attrs={'id': 'id__task_meta'})

        assert 'Characters' in html
        assert 'Protagonist' in html

    def test_render_top_level_items_key(self) -> None:
        widget = JsonTreeWidget()
        value = {'items': [{'name': 'One'}, {'name': 'Two'}]}

        html = widget.render('_task_meta', json.dumps(value), attrs={'id': 'id__task_meta'})

        assert 'One' in html
        assert 'Two' in html

    def test_render_empty_value(self) -> None:
        widget = JsonTreeWidget()

        html = widget.render('_task_meta', '', attrs={'id': 'id__task_meta'})

        assert 'Copy JSON To Clipboard' in html

    def test_render_storybook_meta(self) -> None:
        widget = JsonTreeWidget()

        html = unescape(widget.render('_task_meta', json.dumps(STORYBOOK_META), attrs={'id': 'id__task_meta'}))

        assert 'The Last Taco in the Wasteland' in html
        assert 'The weary owner of El Solitario.' in html
        assert "You're late. But you're here." in html
        assert 'celery@brian-laptop' in html

    def test_render_celery_task_admin_form(self) -> None:
        form = CeleryTaskModelForm(instance=models.CeleryTask(_task_meta=STORYBOOK_META))

        html = form['_task_meta'].as_widget()

        assert 'The Last Taco in the Wasteland' in html
        assert 'A determined 28-year-old woman.' in html
