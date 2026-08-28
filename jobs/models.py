"""
FTP Ops – Job Tracking Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime


# ── Choices ────────────────────────────────────────────────────────────────────

class Specialization(models.TextChoices):
    NETWORKING    = 'Networking',    'Networking'
    CCTV          = 'CCTV',          'CCTV'
    STARLINK      = 'Starlink',      'Starlink'
    CYBERSECURITY = 'Cybersecurity', 'Cybersecurity'
    GENERAL       = 'General',       'General'


class JobType(models.TextChoices):
    INSTALLATION    = 'Installation',    'Installation'
    MAINTENANCE     = 'Maintenance',     'Maintenance'
    SURVEY          = 'Survey',          'Survey'
    TROUBLESHOOTING = 'Troubleshooting', 'Troubleshooting'
    CCTV            = 'CCTV',            'CCTV'
    STARLINK        = 'Starlink',        'Starlink'
    NETWORKING      = 'Networking',      'Networking'
    OTHER           = 'Other',           'Other'


class JobStatus(models.TextChoices):
    ASSIGNED        = 'Assigned',        'Assigned'
    IN_PROGRESS     = 'In Progress',     'In Progress'
    ON_HOLD         = 'On Hold',         'On Hold'
    COMPLETED       = 'Completed',       'Completed'
    REVIEWED_CLOSED = 'Reviewed/Closed', 'Reviewed/Closed'


class Priority(models.TextChoices):
    LOW    = 'Low',    'Low'
    MEDIUM = 'Medium', 'Medium'
    HIGH   = 'High',   'High'
    URGENT = 'Urgent', 'Urgent'


# ── Core Models ────────────────────────────────────────────────────────────────

class Engineer(models.Model):
    full_name      = models.CharField(max_length=150)
    role           = models.CharField(max_length=100)
    phone          = models.CharField(max_length=20, blank=True)
    email          = models.EmailField(blank=True)
    active_status  = models.BooleanField(default=True)
    specialization = models.CharField(
        max_length=20,
        choices=Specialization.choices,
        default=Specialization.GENERAL,
    )

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.specialization})"


class Client(models.Model):
    name         = models.CharField(max_length=200, unique=True)
    phone_number = models.CharField(max_length=50, blank=True)
    email        = models.EmailField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Site(models.Model):
    client    = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sites')
    site_name = models.CharField(max_length=200)
    address   = models.TextField(blank=True)

    class Meta:
        ordering = ['site_name']

    def __str__(self):
        return f"{self.site_name} – {self.client.name}"


def _generate_job_number():
    """Auto-generate JC-YYYY-NNN, incrementing per calendar year."""
    year = timezone.now().year
    prefix = f"JC-{year}-"
    last = (
        JobCard.objects.filter(job_number__startswith=prefix)
        .order_by('job_number')
        .last()
    )
    if last:
        try:
            seq = int(last.job_number.split('-')[-1]) + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1
    return f"{prefix}{seq:03d}"


class JobCard(models.Model):
    job_number = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    client     = models.ForeignKey(Client,   on_delete=models.PROTECT, related_name='jobs')
    site       = models.ForeignKey(Site,     on_delete=models.PROTECT, related_name='jobs')
    title       = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    job_type    = models.CharField(max_length=20, choices=JobType.choices,   default=JobType.OTHER)
    status      = models.CharField(max_length=20, choices=JobStatus.choices, default=JobStatus.ASSIGNED)
    priority    = models.CharField(max_length=10, choices=Priority.choices,  default=Priority.MEDIUM)

    # PDF Template Fields
    device_sn       = models.CharField('Device S/N', max_length=100, blank=True)
    work_start_date = models.DateField('Work Start Date', null=True, blank=True)
    
    risk_height         = models.BooleanField('Working at height', default=False)
    risk_confined_space = models.BooleanField('Working in Confined space', default=False)
    risk_dust_noise     = models.BooleanField('Dust from drilling & noise', default=False)
    
    safety_ladder  = models.BooleanField('Using a step ladder', default=False)
    safety_ppe     = models.BooleanField('Wearing full PPE', default=False)
    safety_mask    = models.BooleanField('Using ear plugs and dust mask', default=False)
    safety_harness = models.BooleanField('Safety harness', default=False)

    assigned_engineers = models.ManyToManyField(Engineer, blank=True, related_name='job_cards')

    date_assigned  = models.DateTimeField(auto_now_add=True)
    due_date       = models.DateField(null=True, blank=True)
    date_completed = models.DateField(null=True, blank=True)

    created_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_jobs')
    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_jobs')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.job_number:
            self.job_number = _generate_job_number()
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.due_date and self.status not in (
            JobStatus.COMPLETED, JobStatus.REVIEWED_CLOSED
        ):
            return self.due_date < datetime.date.today()
        return False

    def __str__(self):
        return f"[{self.job_number}] {self.title}"


class JobStatusHistory(models.Model):
    job_card   = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, choices=JobStatus.choices, blank=True)
    new_status = models.CharField(max_length=20, choices=JobStatus.choices)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp  = models.DateTimeField(auto_now_add=True)
    comment    = models.TextField(blank=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.job_card.job_number}: {self.old_status} → {self.new_status}"


class JobComment(models.Model):
    job_card  = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='comments')
    author    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text      = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Comment on {self.job_card.job_number} by {self.author}"


class JobAttachment(models.Model):
    job_card    = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='attachments')
    file        = models.FileField(upload_to='attachments/%Y/%m/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.job_card.job_number}"

    @property
    def filename(self):
        import os
        return os.path.basename(self.file.name)

    @property
    def is_image(self):
        return self.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))


class TimeLog(models.Model):
    job_card     = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='time_logs')
    engineer     = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name='time_logs')
    start_time   = models.DateTimeField()
    end_time     = models.DateTimeField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ['start_time']

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.hours_worked = round(delta.total_seconds() / 3600, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.engineer.full_name} on {self.job_card.job_number} ({self.hours_worked}h)"
