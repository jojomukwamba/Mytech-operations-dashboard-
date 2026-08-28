from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobs'
    verbose_name = 'Job Tracking'

    def ready(self):
        import jobs.signals  # noqa: F401 – registers signals
