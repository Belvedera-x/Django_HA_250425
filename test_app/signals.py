from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from test_app.models import Task


@receiver(pre_save, sender=Task)
def notify_task_status_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    old_task = Task.objects.get(pk=instance.pk)

    if old_task.status == instance.status:
        return

    if instance.last_notified_status == instance.status:
        return

    subject = f"Task '{instance.title}' status updated"
    message = (
        f"Hello {instance.owner.username},\n\n"
        f"Your task \"{instance.title}\" status has been updated.\n\n"
        f"old status: {old_task.status}\n"
        f"New status: {instance.status}\n"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [instance.owner.email],
    )

    instance.last_notified_status = instance.status