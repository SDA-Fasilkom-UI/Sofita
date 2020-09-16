import base64
import os

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from app.constants import K_REDIS_HIGH_PRIORITY
from app.permissions import TokenPermission
from grader import tasks
from grader.models import Submission
from grader.utils import get_problems_path


@api_view(['GET'])
def check(request):
    return Response({"message": "ok"})


@api_view(['GET'])
def problems(request):
    query = request.GET.get("query", "")

    problems_path = get_problems_path()
    all_dirs = os.listdir(problems_path)

    result_dirs = []
    for dir_ in all_dirs:
        if len(result_dirs) >= 5:
            break

        dir_path = os.path.join(problems_path, dir_)
        if os.path.isdir(dir_path) and query in dir_:
            result_dirs.append(dir_)

    return Response(result_dirs)


@api_view(['POST'])
@permission_classes([TokenPermission])
def grade(request):
    data = request.data

    sub = Submission.objects.filter(
        attempt_number=data['attemptnumber'],
        assignment_id=data['assignmentid'],
        user_id=data['userid']
    ).first()

    if sub is not None:
        return Response({"message": "ok"})

    sub = Submission.objects.create(
        filename=data['filename'],
        problem_name=data["problemname"],
        time_limit=data['timelimit'],
        memory_limit=data['memorylimit'],
        id_number=data['idnumber'],
        user_id=data['userid'],
        attempt_number=data['attemptnumber'],
        assignment_id=data['assignmentid'],
        course_id=data['courseid'],
        activity_id=data['activityid'],
        content=base64.b64decode(data['content']).decode(),
        due_date=data['duedate'],
        cut_off_date=data['cutoffdate'],
        time_modified=data['timemodified']
    )

    tasks.grade_submission.apply_async(
        (sub.id_, sub.assignment_id, sub.course_id,
         sub.activity_id, sub.user_id, sub.attempt_number),
        priority=K_REDIS_HIGH_PRIORITY
    )

    return Response({"message": "ok"})


@api_view(['POST'])
@permission_classes([TokenPermission])
def skip(request):
    data = request.data
    tasks.skip.delay(
        data['assignmentid'],
        data['courseid'],
        data['activityid'],
        data['userid'],
        data['attemptnumber']
    )
    return Response({"message": "ok"})
