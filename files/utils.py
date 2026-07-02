"""
Secure file handling: random storage names, extension checks, size limits.
"""
import os
import uuid

from django.conf import settings


def validate_upload(file_obj):
    """
    Raise ValueError with a user-safe message if the upload is not allowed.
    """
    ext = os.path.splitext(file_obj.name)[1].lstrip(".").lower()
    if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        allowed = ", ".join(sorted(settings.ALLOWED_UPLOAD_EXTENSIONS))
        raise ValueError(
            f"File type '.{ext}' is not allowed. Allowed types: {allowed}"
        )

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_obj.size > max_bytes:
        raise ValueError(
            f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB."
        )


def secure_upload_path(instance, filename):
    """
    Store under uploads/<user_id>/<uuid>.<ext> — avoids guessable paths
    and separates files per user.
    """
    ext = os.path.splitext(filename)[1].lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    return os.path.join("uploads", str(instance.user_id), safe_name)
