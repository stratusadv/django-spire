from django.core.wsgi import get_wsgi_application

from django_spire.knowledge.entry.version.block.entities import TextEditorBlockData, \
    EditorBlock, ListEditorBlockData

get_wsgi_application()

test_list_data = {
    'style': 'checklist',
    'meta': {},
    'items': [
        {
            'content': '',
            'items': [
                {'content': 'test', 'items': [], 'meta': {'checked': True}}
            ],
            'meta': {}
        }
    ]
}

list_editor_block_using_data_obj = EditorBlock(
    type='list',
    order=1,
    data=test_list_data,
    tunes={}
)

list_editor_block_data = ListEditorBlockData(**test_list_data)

list_editor_block_using_data_dict = EditorBlock(
    type='list',
    order=1,
    data=list_editor_block_data,
    tunes={}
)

test_text_data = {
    'text': 'test'
}

text_editor_block_data = TextEditorBlockData(**test_text_data)

text_editor_block = EditorBlock(
    type='text',
    order=1,
    data=test_text_data,
    tunes={}
)


print(text_editor_block)