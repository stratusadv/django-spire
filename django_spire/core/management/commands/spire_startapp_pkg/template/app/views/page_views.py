from django.shortcuts import render

def home_page(request):
    return render(request, 'chapter/page/home_page.html')
# Create your views here.