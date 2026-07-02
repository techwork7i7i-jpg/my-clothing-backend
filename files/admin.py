from django.contrib import admin

from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("original_name", "user", "file_size", "created_at")
    list_filter = ("created_at",)
    search_fields = ("original_name", "user__email")
    readonly_fields = ("created_at", "updated_at")
