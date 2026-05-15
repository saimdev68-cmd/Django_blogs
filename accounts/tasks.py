import logging
from celery import shared_task
from .models import Profile , CustomUser
from django.db import IntegrityError
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def create_profile_task(self, user_id):
    try:
        user = CustomUser.objects.only("id", "username").get(id=user_id)
    except CustomUser.DoesNotExist:
        logger.warning("User not found user_id=%s", user_id)
        return {"status": "not_found"}

    try:
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={"name": user.username}
        )

        logger.info(
            "Profile %s user_id=%s",
            "created" if created else "exists",
            user_id
        )

        return {"status": "success", "created": created}

    except IntegrityError as e:
        logger.exception("Integrity error user_id=%s", user_id)
        raise self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, subject, message, recipient_list):
    if not recipient_list:
        logger.warning("Empty recipient list")
        return {"status": "skipped"}

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False
        )

        logger.info("Email sent to %s", recipient_list)
        return {"status": "sent", "recipients": recipient_list}

    except Exception as e:
        logger.exception(
            "Email failed recipients=%s retry=%s/%s",
            recipient_list,
            self.request.retries,
            self.max_retries
        )
        raise self.retry(exc=e, countdown=60)