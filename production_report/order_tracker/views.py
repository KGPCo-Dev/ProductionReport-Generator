from django.shortcuts import render

def order_tracker_view(request):

    build_id = request.GET.get('search')

    return render(request,'order_tracker/order_tracker_preview.html', { 
        'build_id': build_id
     })
