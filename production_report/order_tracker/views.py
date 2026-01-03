from django.shortcuts import render

def order_tracker_view(request):
    return render(request,'order_tracker/order_tracker_preview.html')

# Create your views here.
