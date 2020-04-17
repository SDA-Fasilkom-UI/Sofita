from django.urls import path

from app import views

urlpatterns = [
    path("", views.hello),
    path("media/<path:filename>", views.media),
]
