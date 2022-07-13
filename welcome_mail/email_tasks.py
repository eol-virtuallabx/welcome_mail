
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from django.conf import settings

from celery import task
from django.core.mail import send_mail
from django.utils.html import strip_tags

from django.template.loader import render_to_string

import logging
logger = logging.getLogger(__name__)

EMAIL_DEFAULT_RETRY_DELAY = 30
EMAIL_MAX_RETRIES = 5

@task(
    queue='edx.lms.core.low',
    default_retry_delay=EMAIL_DEFAULT_RETRY_DELAY,
    max_retries=EMAIL_MAX_RETRIES)
def send_welcome_mail(user_email, subject, html_message, course_id, from_addr):
    """
        Send mail to specific user
    """
    emails = [user_email]
    plain_message = strip_tags(html_message)
    
    mail = send_mail(
        subject,
        plain_message,
        from_addr,
        emails,
        fail_silently=False,
        html_message=html_message)
    logger.info('WelcomeMail - Mail Sent, user_email :{}, course: {}'.format(user_email, course_id))
    return mail