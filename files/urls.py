"""
File API routes.
"""
from django.urls import path

from .views import FileDetailView, FileUploadView, UserFileListView

urlpatterns = [
    path("", UserFileListView.as_view(), name="files-list"),
    path("upload/", FileUploadView.as_view(), name="files-upload"),
    path("<int:pk>/", FileDetailView.as_view(), name="files-detail"),
]
