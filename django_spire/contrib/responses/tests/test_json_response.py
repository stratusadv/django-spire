from django.test import TestCase

import json

from django_spire.contrib.responses.json_response import json_response


class JsonResponseTestCase(TestCase):
    def test_success_response(self):
        response = json_response('success', 'It worked')
        data = json.loads(response.content)
        assert data['type'] == 'success', f"Expected 'success', got {data['type']}"
        assert data['message'] == 'It worked', f"Expected 'It worked', got {data['message']}"

    def test_error_response(self):
        response = json_response('error', 'Something failed')
        data = json.loads(response.content)
        assert data['type'] == 'error', f"Expected 'error', got {data['type']}"
        assert data['message'] == 'Something failed', f"Expected 'Something failed', got {data['message']}"

    def test_info_response(self):
        response = json_response('info', 'FYI')
        data = json.loads(response.content)
        assert data['type'] == 'info', f"Expected 'info', got {data['type']}"

    def test_warning_response(self):
        response = json_response('warning', 'Be careful')
        data = json.loads(response.content)
        assert data['type'] == 'warning', f"Expected 'warning', got {data['type']}"

    def test_returns_json_response(self):
        from django.http import JsonResponse
        response = json_response('success', 'test')
        assert isinstance(response, JsonResponse), f"Expected JsonResponse, got {type(response)}"

    def test_content_type_is_json(self):
        response = json_response('success', 'test')
        assert response['Content-Type'] == 'application/json', \
            f"Expected 'application/json', got {response['Content-Type']}"

    def test_extra_kwargs_included(self):
        response = json_response('success', 'Created', redirect_url='/home/')
        data = json.loads(response.content)
        assert data['redirect_url'] == '/home/', f"Expected '/home/', got {data.get('redirect_url')}"

    def test_multiple_extra_kwargs(self):
        response = json_response('info', 'Details', count=5, items=['a', 'b'])
        data = json.loads(response.content)
        assert data['count'] == 5, f"Expected 5, got {data.get('count')}"
        assert data['items'] == ['a', 'b'], f"Expected ['a', 'b'], got {data.get('items')}"

    def test_invalid_type_raises_value_error(self):
        try:
            json_response('invalid', 'test')
            assert False, "Expected ValueError for invalid type"
        except ValueError:
            pass

    def test_empty_message(self):
        response = json_response('success', '')
        data = json.loads(response.content)
        assert data['message'] == '', f"Expected empty string, got {data['message']}"