"""
File API: upload, list user's files, retrieve one, delete.
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import UploadedFile
from .permissions import IsFileOwner
from .serializers import FileUploadSerializer, UploadedFileSerializer


class FileUploadView(generics.CreateAPIView):
    """
    POST /api/files/upload/
    Multipart form: file=<binary>
    Requires: Authorization: Bearer <access_token>
    """

    serializer_class = FileUploadSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            {
                "success": True,
                "message": "File uploaded successfully.",
                "file": UploadedFileSerializer(instance, context={"request": request}).data,
            },
            status=status.HTTP_201_CREATED,
        )


class UserFileListView(generics.ListAPIView):
    """
    GET /api/files/
    Returns all files belonging to the authenticated user.
    """

    serializer_class = UploadedFileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UploadedFile.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "count": queryset.count(),
                "files": serializer.data,
            }
        )


class FileDetailView(generics.RetrieveDestroyAPIView):
    """
    GET /api/files/<id>/ — file metadata
    DELETE /api/files/<id>/ — remove file from disk and database
    """

    serializer_class = UploadedFileSerializer
    permission_classes = (IsAuthenticated, IsFileOwner)

    def get_queryset(self):
        return UploadedFile.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "file": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        name = instance.original_name
        instance.delete()
        return Response(
            {
                "success": True,
                "message": f'File "{name}" deleted successfully.',
            },
            status=status.HTTP_200_OK,
        )
