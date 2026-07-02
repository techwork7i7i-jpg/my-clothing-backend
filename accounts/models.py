"""
Custom user model — email as login identifier for API consistency.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extends Django's user with email uniqueness.
    Username remains required by AbstractUser; we auto-set it from email on register.
    """

    email = models.EmailField(unique=True, db_index=True)

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email
