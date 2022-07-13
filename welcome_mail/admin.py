from django.contrib import admin

# Register your models here.
from .models import WelcomeMail

class WelcomeMailAdmin(admin.ModelAdmin):
    raw_id_fields = ('sender',)
    list_display = ('course_key', 'subject', 'is_active')
    search_fields = ['course_key', 'subject']
    ordering = ['course_key']

admin.site.register(WelcomeMail, WelcomeMailAdmin)
