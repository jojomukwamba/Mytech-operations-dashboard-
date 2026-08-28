"""
Signal: auto-create JobStatusHistory when JobCard.status changes.
"""
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import JobCard, JobStatusHistory


@receiver(pre_save, sender=JobCard)
def track_status_change(sender, instance, **kwargs):
    if not instance.pk:
        return  # new record – no old status to compare
    try:
        old = JobCard.objects.get(pk=instance.pk)
    except JobCard.DoesNotExist:
        return
    if old.status != instance.status:
        JobStatusHistory.objects.create(
            job_card=instance,
            old_status=old.status,
            new_status=instance.status,
            changed_by=instance.last_updated_by,
            comment='',
        )
