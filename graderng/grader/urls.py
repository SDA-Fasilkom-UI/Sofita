from django.urls import path

from grader import views

urlpatterns = [
    path("api/check/", views.check),
    path("api/problems/", views.problems),
    path("api/grade/", views.grade),
    path("api/skip/", views.skip)
]
