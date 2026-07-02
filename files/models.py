"""
Metadata for user-uploaded files stored on disk (MEDIA_ROOT).
"""
from django.conf import settings
from django.db import models

from .utils import secure_upload_path


class UploadedFile(models.Model):
    """One row per uploaded file; actual bytes live in FileField on disk."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_files",
    )
    file = models.FileField(upload_to=secure_upload_path)
    original_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="Size in bytes")
    content_type = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.original_name} ({self.user_id})"

    def delete(self, *args, **kwargs):
        """Remove physical file from disk when the DB row is deleted."""
        if self.file:
            self.file.delete(save=False)
        super().delete(*args, **kwargs)
