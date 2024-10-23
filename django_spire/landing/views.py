# from django.shortcuts import render
# from django.shortcuts import redirect
from django.template.response import TemplateResponse

# from app.landing import forms
from django_spire.landing.context_data import (
    # contact_us_context_data,
    boneyard_context_data,
    crypt_context_data,
    asylum_context_data,
    wasteland_context_data,
    component_context_data
)
# from app.landing.utils import send_contact_us_email


def home_view(request):
    template = 'landing/page/home_page.html'
    return TemplateResponse(request, template)


# def contact_us_view(request):
#     if request.method == 'POST':
#         form = forms.ContactUsForm(request.POST)
#         if form.is_valid():
#             send_contact_us_email(**form.cleaned_data)
#             return redirect('landing:contact_form_success')
#     else:
#         form = forms.ContactUsForm()
#
#     contact_us_context_data['form'] = form
#     return TemplateResponse(request, template='landing/page/contact_us_page.html', context=contact_us_context_data)


# def contact_us_success_view(request):
#     template = 'landing/page/contact_us_success_page.html'
#     return TemplateResponse(request, template)


def boneyard_view(request):
    template = 'landing/page/boneyard.html'
    return TemplateResponse(request, template, context=boneyard_context_data)


def crypt_view(request):
    template = 'landing/page/crypt.html'
    return TemplateResponse(request, template, context=crypt_context_data)


def asylum_view(request):
    template = 'landing/page/asylum.html'
    return TemplateResponse(request, template, context=asylum_context_data)


def wasteland_view(request):
    template = 'landing/page/wasteland.html'
    return TemplateResponse(request, template, context=wasteland_context_data)
