from django.contrib.auth.models import User
from django.db import models
from openedx.core.lib.html_to_text import html_to_text
from opaque_keys.edx.django.models import CourseKeyField

class WelcomeMail(models.Model):
    """
    Stores information for an email to a course.
    """
    sender = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    subject = models.CharField(max_length=128, blank=True, default='')
    html_message = models.TextField(null=True, blank=True, default='')
    text_message = models.TextField(null=True, blank=True, default='')
    course_key = CourseKeyField(max_length=255, db_index=True, unique=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.subject
