from django.http import JsonResponse

from app import tasks


def add(request):
    tasks.do.delay(1, 2)
    return JsonResponse({"message": "ok"})
