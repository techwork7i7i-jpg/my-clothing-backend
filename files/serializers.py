"""
Serializers for file upload and listing.
"""
from rest_framework import serializers

from .models import UploadedFile
from .utils import validate_upload


class UploadedFileSerializer(serializers.ModelSerializer):
    """Read serializer — exposes metadata and a URL to download the file."""

    file_url = serializers.SerializerMethodField()
    size_mb = serializers.SerializerMethodField()

    class Meta:
        model = UploadedFile
        fields = (
            "id",
            "original_name",
            "file_url",
            "file_size",
            "size_mb",
            "content_type",
            "created_at",
        )
        read_only_fields = fields

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None

    def get_size_mb(self, obj):
        return round(obj.file_size / (1024 * 1024), 2)


class FileUploadSerializer(serializers.ModelSerializer):
    """Write serializer — accepts multipart field `file`."""

    file = serializers.FileField(write_only=True)

    class Meta:
        model = UploadedFile
        fields = ("file",)

    def validate_file(self, value):
        try:
            validate_upload(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def create(self, validated_data):
        upload = validated_data["file"]
        user = self.context["request"].user
        return UploadedFile.objects.create(
            user=user,
            file=upload,
            original_name=upload.name,
            file_size=upload.size,
            content_type=getattr(upload, "content_type", "") or "",
        )
