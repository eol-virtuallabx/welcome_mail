#!/usr/bin/env python
# -- coding: utf-8 --

from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.generic.base import View
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from common.djangoapps.course_modes.models import CourseMode
from common.djangoapps.util.json_request import JsonResponse, JsonResponseBadRequest
from lms.djangoapps.instructor.views.instructor_dashboard import null_applicable_aside_types
from lms.djangoapps.instructor.views.api import require_course_permission, common_exceptions_400, require_post_params
from lms.djangoapps.instructor import permissions
from lms.djangoapps.bulk_email.api import is_bulk_email_feature_enabled
from lms.djangoapps.bulk_email.tasks import _get_course_email_context, _get_source_address
from lms.djangoapps.courseware.courses import get_course_by_id, get_course_with_access, get_course
from lms.djangoapps.courseware.access import has_access
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.verified_track_content.models import VerifiedTrackCohortedCourse
from openedx.core.lib.url_utils import quote_slashes
from openedx.core.lib.xblock_utils import wrap_xblock
from openedx.core.lib.html_to_text import html_to_text
from opaque_keys.edx.keys import CourseKey
from xblock.field_data import DictFieldData
from xblock.fields import ScopeIds
from .models import WelcomeMail
from .email_tasks import send_welcome_mail
from xmodule.html_module import HtmlBlock
from urllib.parse import urlencode
from itertools import cycle
from mock import patch
import json
import uuid
import requests
import logging
import sys

logger = logging.getLogger(__name__)

@transaction.non_atomic_requests
@require_POST
@ensure_csrf_cookie
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@require_course_permission(permissions.EMAIL)
@require_post_params(welcome_subject="subject line", welcome_message="message text", is_active='if mail is enabled')
@common_exceptions_400
def save_email(request, course_id):
    """
        Save configured email in instructor view
    """
    course_key = CourseKey.from_string(course_id)

    if not is_bulk_email_feature_enabled(course_id):
        logger.warning(u'WelcomeMail - Email is not enabled for course %s', course_id)
        return HttpResponseForbidden("Email is not enabled for this course.")

    if not validate_user(request.user, course_id):
        logger.warning('WelcomeMail - User dont have permission, user: {}, course: {}'.format(request.user, course_id))
        return HttpResponseForbidden("Email is not enabled for this course.")
    subject = request.POST.get("welcome_subject")
    message = request.POST.get("welcome_message")
    text_message = html_to_text(message)
    try:
        data = {
            'sender': request.user,
            'is_active': request.POST['is_active'] == 'true'
        }
        if data['is_active']:
            data.update({
                'subject': subject,
                'html_message': message,
                'text_message': text_message
            })
        WelcomeMail.objects.update_or_create(
                course_key=course_key,
                defaults=data)
    except ValueError as err:
        logger.exception(u'WelcomeMail - Cannot create welcome mail for course %s requested by user %s',
                      course_id, request.user)
        return HttpResponseBadRequest(repr(err))

    response_payload = {
        'result': 'success',
    }

    return JsonResponse(response_payload)

def send_email(user_email, course_key):
    """
        Send configured email in instructor view
    """
    if WelcomeMail.objects.filter(course_key=course_key, is_active=True).exists():
        mail = WelcomeMail.objects.get(course_key=course_key)
        from_addr = configuration_helpers.get_value('course_email_from_addr', '')
        if isinstance(from_addr, dict):
            from_addr = from_addr.get(mail.course_key.org)
        if not from_addr:
            course = get_course(course_key)
            global_email_context = _get_course_email_context(course)
            course_title = global_email_context['course_title']
            course_language = global_email_context['course_language']
            from_addr = _get_source_address(course_key, course_title, course_language)
        send_welcome_mail.delay(user_email, mail.subject, mail.html_message, str(course_key), from_addr)

def is_course_staff(user, course_id):
    """
        Verify if the user is staff course
    """
    try:
        course_key = CourseKey.from_string(course_id)
        course = get_course_with_access(user, "load", course_key)

        return bool(has_access(user, 'staff', course))
    except Exception:
        return False

def is_instructor(user, course_id):
    """
        Verify if the user is instructor
    """
    try:
        course_key = CourseKey.from_string(course_id)
        course = get_course_with_access(user, "load", course_key)

        return bool(has_access(user, 'instructor', course))
    except Exception:
        return False

def validate_user(user, course_id):
    """
        Verify if the user have permission
    """
    access = False
    if not user.is_anonymous:
        if user.is_staff:
            access = True
        if is_instructor(user, course_id):
            access = True
        if is_course_staff(user, course_id):
            access = True
    return access