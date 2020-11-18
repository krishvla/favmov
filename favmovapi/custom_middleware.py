from django.db.models import F
from .models import RequestCount

def CountRequests(get_response):
    def middleware(request):
        print("Hello")
        check = RequestCount.objects.all()
        if check:
            RequestCount.objects.all().update(count = F('count') + 1)
        else:
            req_obj = RequestCount()
            req_obj.count = 1
            req_obj.save()

        response = get_response(request)
        return response

    return middleware