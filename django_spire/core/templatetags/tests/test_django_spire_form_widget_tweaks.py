from __future__ import annotations

import unittest

from django import forms
from django.forms import CharField, IntegerField, Textarea
from django.template import Context, Template

from django_spire.core.templatetags.django_spire_form_widget_tweaks import (
    add_class,
    add_error_attr,
    add_error_class,
    add_label_class,
    add_required_class,
    append_attr,
    field_type,
    remove_attr,
    set_attr,
    set_data,
    widget_type,
)


class TestSetAttr(unittest.TestCase):
    def setUp(self) -> None:
        class TestForm(forms.Form):
            name = CharField()

        self.form = TestForm()

    def test_sets_attribute(self) -> None:
        field = self.form['name']
        result = set_attr(field, 'placeholder:Enter name')

        assert 'placeholder="Enter name"' in str(result)

    def test_sets_multiple_attributes(self) -> None:
        field = self.form['name']
        result = set_attr(field, 'id:test-id')

        assert 'id="test-id"' in str(result)


class TestAddErrorAttr(unittest.TestCase):
    def setUp(self) -> None:
        class TestForm(forms.Form):
            name = CharField()

        self.form = TestForm()

    def test_adds_attr_when_field_has_errors(self) -> None:
        self.form = self.form.__class__(data={'name': 'test'})
        self.form.is_valid()
        self.form.add_error('name', 'error')
        field = self.form['name']
        result = add_error_attr(field, 'class:error-field')

        assert 'error-field' in str(result)

    def test_does_nothing_when_no_errors(self) -> None:
        field = self.form['name']
        result = add_error_attr(field, 'class:error-field')

        assert 'error-field' not in str(result)


class TestAppendAttr(unittest.TestCase):
    def setUp(self) -> None:
        class TestForm(forms.Form):
            name = CharField()

        self.form = TestForm()

    def test_appends_to_existing_attr(self) -> None:
        field = self.form['name']
        field.field.widget.attrs['class'] = 'first'
        result = append_attr(field, 'class:second')

        assert 'first second' in str(result)

    def test_creates_attr_when_none_exists(self) -> None:
        field = self.form['name']
        result = append_attr(field, 'data-test:value')

        assert 'data-test="value"' in str(result)


class TestAddClass(unittest.TestCase):
    def setUp(self) -> None:
        class TestForm(forms.Form):
            name = CharField()

        self.form = TestForm()

    def test_adds_class(self) -> None:
        field = self.form['name']
        result = add_class(field, 'my-class')

        assert 'my-class' in str(result)

    def test_preserves_existing_classes(self) -> None:
        field = self.form['name']
        field.field.widget.attrs['class'] = 'existing'
        result = add_class(field, 'new-class')

        output = str(result)
        assert 'existing' in output
        assert 'new-class' in output


class TestAddLabelClass(unittest.TestCase):
    def setUp(self) -> None:
        class TestForm(forms.Form):
            name = CharField()

        self.form = TestForm()

    def test_adds_class_to_label(self) -> None:
        field = self.form['name']
        result = add_label_class(field, 'custom-label')

        assert 'custom-label' in result


class TestAddErrorClass(unittest.TestCase):
    def setUp(self) -> None:
        class TestForm(forms.Form):
            name = CharField()

        self.form = TestForm()

    def test_adds_error_class_when_field_has_errors(self) -> None:
        self.form = self.form.__class__(data={'name': 'test'})
        self.form.is_valid()
        self.form.add_error('name', 'error')
        field = self.form['name']
        result = add_error_class(field, 'is-invalid')

        assert 'is-invalid' in str(result)

    def test_does_nothing_when_no_errors(self) -> None:
        field = self.form['name']
        result = add_error_class(field, 'is-invalid')

        assert 'is-invalid' not in str(result)


class TestAddRequiredClass(unittest.TestCase):
    def setUp(self) -> None:
        class TestForm(forms.Form):
            name = CharField(required=True)
            optional = CharField(required=False)

        self.form = TestForm()

    def test_adds_class_to_required_field(self) -> None:
        field = self.form['name']
        result = add_required_class(field, 'required-field')

        assert 'required-field' in str(result)

    def test_does_nothing_for_optional_field(self) -> None:
        field = self.form['optional']
        result = add_required_class(field, 'required-field')

        assert 'required-field' not in str(result)


class TestSetData(unittest.TestCase):
    def setUp(self) -> None:
        class TestForm(forms.Form):
            name = CharField()

        self.form = TestForm()

    def test_sets_data_attribute(self) -> None:
        field = self.form['name']
        result = set_data(field, 'test:value')

        assert 'data-test="value"' in str(result)

    def test_handles_nested_data(self) -> None:
        field = self.form['name']
        result = set_data(field, 'custom-key:custom-value')

        assert 'data-custom-key="custom-value"' in str(result)


class TestFieldType(unittest.TestCase):
    def setUp(self) -> None:
        class TestForm(forms.Form):
            text = CharField()
            number = IntegerField()
            area = CharField(widget=Textarea)

        self.form = TestForm()

    def test_returns_charfield(self) -> None:
        assert field_type(self.form['text']) == 'charfield'

    def test_returns_integerfield(self) -> None:
        assert field_type(self.form['number']) == 'integerfield'

    def test_returns_charfield_for_textarea_widget(self) -> None:
        assert field_type(self.form['area']) == 'charfield'

    def test_returns_empty_for_none_field(self) -> None:
        class FakeBoundField:
            field = None

        assert field_type(FakeBoundField()) == ''


class TestWidgetType(unittest.TestCase):
    def setUp(self) -> None:
        class TestForm(forms.Form):
            text = CharField()
            area = CharField(widget=Textarea)

        self.form = TestForm()

    def test_returns_text_input(self) -> None:
        assert widget_type(self.form['text']) == 'textinput'

    def test_returns_textarea(self) -> None:
        assert widget_type(self.form['area']) == 'textarea'

    def test_returns_empty_for_none_widget(self) -> None:
        class FakeBoundField:
            field = None

        assert widget_type(FakeBoundField()) == ''


class TestRemoveAttr(unittest.TestCase):
    def setUp(self) -> None:
        class TestForm(forms.Form):
            name = CharField()

        self.form = TestForm()

    def test_removes_existing_attr(self) -> None:
        field = self.form['name']
        field.field.widget.attrs['data-id'] = '123'
        result = remove_attr(field, 'data-id')

        assert 'data-id' not in result.field.widget.attrs

    def test_handles_missing_attr(self) -> None:
        field = self.form['name']
        result = remove_attr(field, 'data-id')

        assert result is not None


class TestRenderFieldTag(unittest.TestCase):
    def setUp(self) -> None:
        class TestForm(forms.Form):
            name = CharField(required=True)
            email = CharField(required=False)

        self.form = TestForm()

    def test_render_field_basic(self) -> None:
        template_code = """
            {% load django_spire_form_widget_tweaks %}

            {% render_field form.name %}
        """

        tmpl = Template(template_code)
        context = Context({'form': self.form})
        rendered = tmpl.render(context)

        assert '<input' in rendered
        assert 'name="name"' in rendered

    def test_render_field_with_class(self) -> None:
        template_code = """
            {% load django_spire_form_widget_tweaks %}

            {% render_field form.name class="form-control" %}
        """

        tmpl = Template(template_code)
        context = Context({'form': self.form})
        rendered = tmpl.render(context)

        assert 'form-control' in rendered

    def test_render_field_with_placeholder(self) -> None:
        template_code = """
            {% load django_spire_form_widget_tweaks %}

            {% render_field form.name placeholder="Enter your name" %}
        """

        tmpl = Template(template_code)
        context = Context({'form': self.form})
        rendered = tmpl.render(context)

        assert 'placeholder="Enter your name"' in rendered

    def test_render_field_with_data_attr(self) -> None:
        template_code = """
            {% load django_spire_form_widget_tweaks %}

            {% render_field form.name data-id="123" %}
        """

        tmpl = Template(template_code)
        context = Context({'form': self.form})
        rendered = tmpl.render(context)

        assert 'data-id="123"' in rendered

    def test_render_field_with_multiple_attrs(self) -> None:
        template_code = """
            {% load django_spire_form_widget_tweaks %}

            {% render_field form.name class="input" id="name-field" placeholder="Name" %}
        """

        tmpl = Template(template_code)
        context = Context({'form': self.form})
        rendered = tmpl.render(context)

        assert 'input' in rendered
        assert 'name-field' in rendered
        assert 'Name' in rendered

    def test_render_field_with_type_override(self) -> None:
        template_code = """
            {% load django_spire_form_widget_tweaks %}

            {% render_field form.name type="text" %}
        """

        tmpl = Template(template_code)
        context = Context({'form': self.form})
        rendered = tmpl.render(context)

        assert 'type="text"' in rendered

    def test_render_field_with_append_attr(self) -> None:
        template_code = """
            {% load django_spire_form_widget_tweaks %}

            {% render_field form.name class+="extra-class" %}
        """

        tmpl = Template(template_code)
        context = Context({'form': self.form})
        rendered = tmpl.render(context)

        assert 'extra-class' in rendered

    def test_render_field_silent_on_none(self) -> None:
        template_code = """
            {% load django_spire_form_widget_tweaks %}

            {% render_field form.name %}
        """

        tmpl = Template(template_code)
        context = Context({'form': None})
        rendered = tmpl.render(context)

        assert rendered.strip() == ''
