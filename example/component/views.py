from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.template.response import TemplateResponse

from django_glue.glue import glue_model

from django_spire.shortcuts import get_object_or_null_obj

from example.component.utils import from_directory, from_file
from example.cookbook.models import Cookbook

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'page/component.html'
    return TemplateResponse(request, template)


def accordion_view(request: WSGIRequest) -> TemplateResponse:
    exclude_template = ['accordion']

    example = from_file('example/templates/component/accordion/example_accordion.html')

    gallery = from_directory(
        'django_spire/templates/spire/accordion/',
        exclude_template=exclude_template
    )

    context = {'example': example, 'gallery': gallery}

    template = 'component/accordion/accordion.html'
    return TemplateResponse(request, template, context)


def badge_view(request: WSGIRequest) -> TemplateResponse:
    exclude_template = ['base_badge']

    example = from_file('example/templates/component/badge/example_badge.html')

    gallery = from_directory(
        'django_spire/templates/spire/badge/',
        badge_text='Sample Text',
        exclude_template=exclude_template
    )

    context = {'example': example, 'gallery': gallery}

    template = 'component/badge/badge.html'
    return TemplateResponse(request, template, context)


def base_view(request: WSGIRequest) -> TemplateResponse:
    template = 'component/base/base.html'
    return TemplateResponse(request, template)


def button_view(request: WSGIRequest) -> TemplateResponse:
    cookbook = get_object_or_null_obj(Cookbook, pk=1)
    glue_model(request, 'cookbook', cookbook)

    exclude_template = ['base_button']

    example = from_file('example/templates/component/button/example_button.html')

    gallery = from_directory(
        'django_spire/templates/spire/button/',
        button_text='Sample Text',
        exclude_template=exclude_template
    )

    context = {
        'cookbook': cookbook,
        'example': example,
        'gallery': gallery,
    }

    template = 'component/button/button.html'
    return TemplateResponse(request, template, context)


def card_view(request: WSGIRequest) -> TemplateResponse:
    exclude_template = [
        # No output/lack of context data
        'card',
        'form_card',
        'title_card'
    ]

    example = from_file('example/templates/component/card/example_card.html')

    gallery = from_directory(
        'django_spire/templates/spire/card/',
        exclude_template=exclude_template
    )

    context = {'example': example, 'gallery': gallery}

    template = 'component/card/card.html'
    return TemplateResponse(request, template, context)


def comment_view(request: WSGIRequest) -> TemplateResponse:
    # @TODO: Fix missing templates

    exclude_template = [
        # These include/extend templates that do not exist
        'comment_card',
        'comment_edit_link',
        'comment_edit_modal',
        'comment_item',
        'comment_item_ellipsis',
        'comment_modal',
        'comment_reply_element',
        'comment_reply_link',
        'comment_reply_modal',
        'comment_textarea_card',
        'comment_textarea_element',

        # No output/lack of context data
        'comment_reply_list_container',
        'comment_button_element'
    ]

    context = {}

    template = 'component/comment/comment.html'
    return TemplateResponse(request, template, context)


def container_view(request: WSGIRequest) -> TemplateResponse:
    exclude_template = [
        # No output/lack of context data
        'container',
        'form_container'
    ]

    example = from_file('example/templates/component/container/example_container.html')

    gallery = from_directory(
        'django_spire/templates/spire/container/',
        exclude_template=exclude_template
    )

    context = {'example': example, 'gallery': gallery}

    template = 'component/container/container.html'
    return TemplateResponse(request, template, context)


def dropdown_view(request: WSGIRequest) -> TemplateResponse:
    exclude_template = [
        # No output/lack of context data
        'dropdown',
        'dropdown_link_element',
        'ellipsis_dropdown',
        'ellipsis_modal_dropdown',
        'ellipsis_dropdown_modal_link_element'
    ]

    example = from_file('example/templates/component/dropdown/example_dropdown.html')

    gallery = from_directory(
        'django_spire/templates/spire/dropdown/',
        exclude_template=exclude_template
    )

    context = {'example': example, 'gallery': gallery}

    template = 'component/dropdown/dropdown.html'
    return TemplateResponse(request, template, context)


def element_view(request: WSGIRequest) -> TemplateResponse:
    exclude_template = [
        # No output/lack of context data
        'attribute_element',
        'breadcrumb_element',
        'divider_element',
        'page_loading_element',

        'pagination_element'
    ]

    example = from_file('example/templates/component/element/example_element.html')

    gallery = from_directory(
        'django_spire/templates/spire/element/',
        exclude_template=exclude_template
    )

    context = {'example': example, 'gallery': gallery}

    template = 'component/element/element.html'
    return TemplateResponse(request, template, context)


def file_view(request: WSGIRequest) -> TemplateResponse:
    # @TODO: Fix missing templates

    exclude_template = [
        # These include/extend templates that do not exist
        'demo_detail_page',
        'file_navigation',
        'multiple_file_widget',
        'single_file_widget',
        'version_list_page',

        # No output/lack of context data
        'demo_detail_card',
        'demo_item',
        'file_item',

        # django_glue/keep-alive issue
        'demo_list_page',
    ]

    example = from_file('example/templates/component/file/example_file.html')

    gallery = from_directory(
        'django_spire/templates/spire/file/',
        exclude_template=exclude_template
    )

    context = {'example': example, 'gallery': gallery}

    template = 'component/file/file.html'
    return TemplateResponse(request, template, context)


def form_view(request: WSGIRequest) -> TemplateResponse:
    # @TODO: Fix missing templates

    exclude_template = [
        # These include/extend templates that do not exist
        'input_field',
        'search_select_form_field'
    ]

    example = from_file('example/templates/component/form/example_form.html')

    gallery = from_directory(
        'django_spire/templates/spire/form/',
        exclude_template=exclude_template
    )

    context = {'example': example, 'gallery': gallery}

    template = 'component/form/form.html'
    return TemplateResponse(request, template, context)


def help_view(request: WSGIRequest) -> TemplateResponse:
    exclude_template = ['help_button', 'help_modal']

    gallery = from_directory(
        'django_spire/templates/spire/help/',
        exclude_template=exclude_template
    )

    example = from_file('example/templates/component/help/example_help.html')

    context = {'example': example, 'gallery': gallery}

    template = 'component/help/help.html'
    return TemplateResponse(request, template, context)


def item_view(request: WSGIRequest) -> TemplateResponse:
    exclude_template = ['item', 'item_ellipsis_spacer_element']

    example = from_file('example/templates/component/item/example_item.html')

    gallery = from_directory(
        'django_spire/templates/spire/item/',
        exclude_template=exclude_template
    )

    context = {'example': example, 'gallery': gallery}

    template = 'component/item/item.html'
    return TemplateResponse(request, template, context)


def modal_view(request: WSGIRequest) -> TemplateResponse:
    exclude_template = [
        'center_modal',
        'dispatch_modal',
        'modal',
        'title_modal',
        'modal_title_content'
    ]

    example = from_file('example/templates/component/modal/example_modal.html')

    gallery = from_directory(
        'django_spire/templates/spire/modal/',
        exclude_template=exclude_template
    )

    context = {'example': example, 'gallery': gallery}

    template = 'component/modal/modal.html'
    return TemplateResponse(request, template, context)


def modal_content_view(request: WSGIRequest) -> TemplateResponse:
    template = 'component/modal/modal_content.html'
    return TemplateResponse(request, template)


def navigation_view(request: WSGIRequest) -> TemplateResponse:
    exclude_template = [
        # Broken
        'search_bar_element',

        # No output/lack of context data
        'mobile_navigation',
        'side_navigation'
    ]

    example = from_file('example/templates/component/navigation/example_navigation.html')

    gallery = from_directory(
        'django_spire/templates/spire/navigation/',
        exclude_template=exclude_template
    )

    context = {'example': example, 'gallery': gallery}

    template = 'component/navigation/navigation.html'
    return TemplateResponse(request, template, context)


def notification_view(request: WSGIRequest) -> TemplateResponse:
    exclude_template = ['notification', 'notification_element']

    example = from_file('example/templates/component/notification/example_notification.html')

    gallery = from_directory(
        'django_spire/templates/spire/notification/',
        exclude_template=exclude_template
    )

    context = {'example': example, 'gallery': gallery}

    template = 'component/notification/notification.html'
    return TemplateResponse(request, template, context)


def page_view(request: WSGIRequest) -> TemplateResponse:
    exclude_template = [
        # No output/lack of context data
        'base_page',
        'center_card_page',
        'form_full_page',

        # django_glue/keep-alive issue
        'full_page'
    ]

    gallery = from_directory(
        'django_spire/templates/spire/page/',
        exclude_template=exclude_template
    )

    context = {'gallery': gallery}

    template = 'component/page/_page.html'
    return TemplateResponse(request, template, context)


def tab_view(request: WSGIRequest) -> TemplateResponse:
    exclude_template = [
        # No output/lack of context data
        'tab',
        'tab_section_element',
        'tab_trigger_element'
    ]

    example = from_file('example/templates/component/tab/example_tab.html')

    gallery = from_directory(
        'django_spire/templates/spire/tab/',
        exclude_template=exclude_template
    )

    context = {'example': example, 'gallery': gallery}

    template = 'component/tab/tab.html'
    return TemplateResponse(request, template, context)
