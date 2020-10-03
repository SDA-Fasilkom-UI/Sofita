import mimetypes
import os

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.http import (
    Http404,
    FileResponse,
    StreamingHttpResponse
)
from django.shortcuts import render


def hello(request):
    return render(request, "homepage.html", {})


@user_passes_test(lambda u: u.is_staff, login_url="admin:login")
def media(request, filename):
    """
    View to access media with login required.
    """

    path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.isfile(path):
        type_, _ = mimetypes.guess_type(path)
        if type_:
            return FileResponse(open(path, "rb"))
        else:
            return StreamingHttpResponse(open(path), content_type="text/plain")

    raise Http404()
