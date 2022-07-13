#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mock import patch, Mock, MagicMock
from collections import namedtuple
from django.urls import reverse
from django.test import TestCase, Client
from django.test import Client
from django.conf import settings
from django.contrib.auth.models import Permission, User
from urllib.parse import parse_qs
from opaque_keys.edx.locator import CourseLocator
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from common.djangoapps.student.tests.factories import CourseEnrollmentAllowedFactory, UserFactory, CourseEnrollmentFactory
from common.djangoapps.student.roles import CourseInstructorRole, CourseStaffRole
from lms.djangoapps.bulk_email.models import BulkEmailFlag, CourseAuthorization
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from .models import WelcomeMail
from .views import send_email
import re
import json
import urllib.parse
# Create your tests here.


class TestWelcomeMailView(ModuleStoreTestCase):

    def setUp(self):
        super(TestWelcomeMailView, self).setUp()
        self.course = CourseFactory.create(
            org='mss',
            course='999',
            display_name='2020',
            emit_signals=True)
        aux = CourseOverview.get_from_id(self.course.id)
        with patch('common.djangoapps.student.models.cc.User.save'):
            # user instructor
            self.client_instructor = Client()
            self.user_instructor = UserFactory(
                username='instructor',
                password='12345',
                email='instructor@edx.org')
            role = CourseInstructorRole(self.course.id)
            role.add_users(self.user_instructor)
            self.client_instructor.login(
                username='instructor', password='12345')

            # user student
            self.student_client = Client()
            self.student = UserFactory(
                username='student',
                password='12345',
                email='student@edx.org')
            CourseEnrollmentFactory(
                user=self.student, course_id=self.course.id)
            self.assertTrue(
                self.student_client.login(
                    username='student',
                    password='12345'))
            
    def test_save_email(self):
        """
            test save email
        """
        BulkEmailFlag.objects.create(enabled=True, require_course_email_auth=True)
        cauth = CourseAuthorization(course_id=self.course.id, email_enabled=True)
        cauth.save()
        post_data = {
            'is_active': "true",
            'welcome_subject': 'this is a subject',
            'welcome_message': "<p>asdas dsadas dasdasd</p>"
        }
        self.assertEqual(len(WelcomeMail.objects.all()), 0)
        response = self.client_instructor.post(reverse('welcome-mail:save', kwargs={'course_id': str(self.course.id)}), post_data)
        self.assertEqual(response.status_code, 200)
        r = json.loads(response._container[0].decode())
        self.assertEqual(r['result'], 'success')
        mail = WelcomeMail.objects.get(course_key=self.course.id)
        self.assertEqual(mail.is_active, True)
        self.assertEqual(mail.subject, post_data['welcome_subject'])
        self.assertEqual(mail.html_message, post_data['welcome_message'])
        self.assertEqual(mail.sender, self.user_instructor)

    def test_save_email_disabled_mail(self):
        """
            test save email when disable welcome mail
        """
        BulkEmailFlag.objects.create(enabled=True, require_course_email_auth=True)
        cauth = CourseAuthorization(course_id=self.course.id, email_enabled=True)
        cauth.save()
        post_data = {
            'is_active': "false",
            'welcome_subject': 'this is a subject',
            'welcome_message': "<p>asdas dsadas dasdasd</p>"
        }
        self.assertEqual(len(WelcomeMail.objects.all()), 0)
        response = self.client_instructor.post(reverse('welcome-mail:save', kwargs={'course_id': str(self.course.id)}), post_data)
        self.assertEqual(response.status_code, 200)
        r = json.loads(response._container[0].decode())
        self.assertEqual(r['result'], 'success')
        mail = WelcomeMail.objects.get(course_key=self.course.id)
        self.assertEqual(mail.is_active, False)
        self.assertEqual(mail.subject, '')
        self.assertEqual(mail.html_message, '')
        self.assertEqual(mail.sender, self.user_instructor)

    def test_save_email_disabled_mail_2(self):
        """
            test save email when disable welcome mail and exists mail model
        """
        WelcomeMail.objects.update_or_create(
            course_key=self.course.id,
            defaults={
                'sender': self.user_instructor, 
                'subject': 'this is a subject',
                'html_message': "<p>asdas dsadas dasdasd</p>",
                'text_message': "asdas dsadas dasdasd",
                'is_active': True
                })
        BulkEmailFlag.objects.create(enabled=True, require_course_email_auth=True)
        cauth = CourseAuthorization(course_id=self.course.id, email_enabled=True)
        cauth.save()
        post_data = {
            'is_active': "false",
            'welcome_subject': 'adsasdasdad',
            'welcome_message': "asdasdsadadasd"
        }
        response = self.client_instructor.post(reverse('welcome-mail:save', kwargs={'course_id': str(self.course.id)}), post_data)
        self.assertEqual(response.status_code, 200)
        r = json.loads(response._container[0].decode())
        self.assertEqual(r['result'], 'success')
        mail = WelcomeMail.objects.get(course_key=self.course.id)
        self.assertEqual(mail.is_active, False)
        self.assertEqual(mail.subject, 'this is a subject')
        self.assertEqual(mail.html_message, "<p>asdas dsadas dasdasd</p>")
        self.assertEqual(mail.sender, self.user_instructor)

    def test_save_email_user_anonymous(self):
        """
            Test if the user is anonymous
        """
        BulkEmailFlag.objects.create(enabled=True, require_course_email_auth=True)
        cauth = CourseAuthorization(course_id=self.course.id, email_enabled=True)
        cauth.save()
        post_data = {
            'is_active': "true",
            'welcome_subject': 'this is a subject',
            'welcome_message': "asdas dsadas dasdasd"
        }
        client = Client()
        response = client.post(reverse('welcome-mail:save', kwargs={'course_id': str(self.course.id)}), post_data)
        self.assertEqual(response.status_code, 403)
    
    def test_save_email_student(self):
        """
            Test if the user is student
        """
        BulkEmailFlag.objects.create(enabled=True, require_course_email_auth=True)
        cauth = CourseAuthorization(course_id=self.course.id, email_enabled=True)
        cauth.save()
        post_data = {
            'is_active': "true",
            'welcome_subject': 'this is a subject',
            'welcome_message': "asdas dsadas dasdasd"
        }
        response = self.student_client.post(reverse('welcome-mail:save', kwargs={'course_id': str(self.course.id)}), post_data)
        self.assertEqual(response.status_code, 403)

    def test_save_email_bulk_disabeld(self):
        """
            Test save email when bulk email is disabled
        """
        BulkEmailFlag.objects.create(enabled=True, require_course_email_auth=True)
        cauth = CourseAuthorization(course_id=self.course.id, email_enabled=False)
        cauth.save()
        post_data = {
            'is_active': "true",
            'welcome_subject': 'this is a subject',
            'welcome_message': "asdas dsadas dasdasd"
        }
        response = self.client_instructor.post(reverse('welcome-mail:save', kwargs={'course_id': str(self.course.id)}), post_data)
        self.assertEqual(response.status_code, 403)
    
    def test_save_email_no_params(self):
        """
            Test save email with no params
        """
        BulkEmailFlag.objects.create(enabled=True, require_course_email_auth=True)
        cauth = CourseAuthorization(course_id=self.course.id, email_enabled=True)
        cauth.save()
        post_data = {
            'is_active': "true",
            'welcome_message': "asdas dsadas dasdasd"
        }
        response = self.client_instructor.post(reverse('welcome-mail:save', kwargs={'course_id': str(self.course.id)}), post_data)
        self.assertEqual(response.status_code, 400)
    
    def test_save_email_wrong_course_id(self):
        """
            Test save email when course id is wrong
        """
        BulkEmailFlag.objects.create(enabled=True, require_course_email_auth=True)
        cauth = CourseAuthorization(course_id=self.course.id, email_enabled=True)
        cauth.save()
        post_data = {
            'is_active': "true",
            'welcome_subject': 'this is a subject',
            'welcome_message': "asdas dsadas dasdasd"
        }
        response = self.client_instructor.post(reverse('welcome-mail:save', kwargs={'course_id': 'course-v1:eol+Test101+2021'}), post_data)
        self.assertEqual(response.status_code, 404)

    def test_send_email(self):
        """
            Test send email
        """
        WelcomeMail.objects.update_or_create(
            course_key=self.course.id,
            defaults={
                'sender': self.user_instructor, 
                'subject': 'this is a subject',
                'html_message': "<p>asdas dsadas dasdasd</p>",
                'text_message': "asdas dsadas dasdasd",
                'is_active': True
                })
        send_email(self.user_instructor.email, self.course.id)