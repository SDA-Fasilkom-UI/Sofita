import base64

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from app import tasks
from app.models import Submission
from app.permissions import TokenPermission


@api_view(['POST'])
@permission_classes([TokenPermission])
def grade(request):
    data = request.data
    sub = Submission.objects.create(
        filename=data['filename'],
        problem_name=data["problemname"],
        time_limit=data['timelimit'],
        memory_limit=data['memorylimit'],
        id_number=data['idnumber'],
        user_id=data['userid'],
        attempt_number=data['attemptnumber'],
        assignment_id=data['assignmentid'],
        content=base64.b64decode(data['content']).decode(),
        due_date=data['duedate'],
        cut_off_date=data['cutoffdate'],
        time_modified=data['timemodified']
    )

    tasks.grade.delay(sub.id, sub.assignment_id,
                      sub.user_id, sub.attempt_number)

    return Response({"message": "ok"})


@api_view(['POST'])
@permission_classes([TokenPermission])
def skip(request):
    data = request.data
    assignment_id = data['assignmentid']
    user_id = data['userid']
    attempt_number = data['attemptnumber']

    tasks.skip.delay(assignment_id, user_id, attempt_number)

    return Response({"message": "ok"})


def hello(request):
    return HttpResponse("Hello")
