from django.contrib import admin
from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required
from .views import save_email


urlpatterns = [
    url('save/', save_email, name='save'),
]
