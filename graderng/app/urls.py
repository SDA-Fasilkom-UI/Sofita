from django.urls import path

from app import views

urlpatterns = [
    path("", views.hello),
    path("api/grade/", views.grade),
    path("api/skip/", views.skip)
]
