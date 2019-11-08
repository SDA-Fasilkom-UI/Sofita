from django.urls import path

from app import views

urlpatterns = [
    path("grade/", views.grade),
    path("skip/", views.skip)
]
