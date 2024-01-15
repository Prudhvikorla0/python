"""
Email Integrations
"""
import logging
from sentry_sdk import capture_exception
from celery import shared_task

from django.conf import settings
from django.core.mail import send_mail

from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


@shared_task(name='send_email')
def send_email(subject, to_email, html):
    """Function to create Validator email."""

    try:
        send_mail(
            subject=subject,
            message=strip_tags(html),
            from_email=settings.FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html)
        logger.info('Email sending success.')
    except Exception as e:
        capture_exception(e)
        logger.info('Email sending failed.')
    return True

