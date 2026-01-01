from django.shortcuts import render

def home_view(request):
    return render(request, 'home/home_preview.html')
# Create your views here.
