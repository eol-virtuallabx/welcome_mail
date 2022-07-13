# Welcome Mail

![https://github.com/eol-uchile/eol_welcome_mail/actions](https://github.com/eol-uchile/eol_welcome_mail/workflows/Python%20application/badge.svg)

Send email to student when they enroll in the course

# Install App

    docker-compose exec lms pip install -e /openedx/requirements/eol_welcome_mail
    docker-compose exec lms_worker pip install -e /openedx/requirements/eol_welcome_mail
    docker-compose exec lms python manage.py lms --settings=prod.production makemigrations welcome_mail
    docker-compose exec lms python manage.py lms --settings=prod.production migrate welcome_mail

## TESTS
**Prepare tests:**

    > cd .github/
    > docker-compose run lms /openedx/requirements/welcome_mail/.github/test.sh
