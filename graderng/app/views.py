from django.http import HttpResponse


def hello(request):
    response = \
        """
        Hello <br>
        <button onclick="window.location.href = '/admin';">
            Go to Admin Page
        </button>
        """

    return HttpResponse(response)
