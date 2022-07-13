#!/bin/dash
pip install -e /openedx/requirements/welcome_mail

cd /openedx/requirements/welcome_mail
cp /openedx/edx-platform/setup.cfg .
mkdir test_root
cd test_root/
ln -s /openedx/staticfiles .

cd /openedx/requirements/welcome_mail

DJANGO_SETTINGS_MODULE=lms.envs.test EDXAPP_TEST_MONGO_HOST=mongodb pytest welcome_mail/tests.py
