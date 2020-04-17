import mimetypes
import os

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import (
    Http404,
    HttpResponse,
    FileResponse,
    StreamingHttpResponse
)


def hello(request):
    response = \
        """
        Hello <br>
        <button onclick="window.location.href = '/admin';">
            Go to Admin Page
        </button>
        """

    return HttpResponse(response)


@login_required(login_url="/admin/")
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
