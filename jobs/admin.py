from django.contrib import admin
from .models import Engineer, Client, Site, JobCard, JobStatusHistory, JobComment, JobAttachment


@admin.register(Engineer)
class EngineerAdmin(admin.ModelAdmin):
    list_display  = ('full_name', 'specialization', 'role', 'phone', 'email', 'active_status')
    list_filter   = ('specialization', 'active_status')
    search_fields = ('full_name', 'email', 'role')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display  = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display  = ('site_name', 'client', 'address')
    list_filter   = ('client',)
    search_fields = ('site_name', 'address', 'client__name')


class StatusHistoryInline(admin.TabularInline):
    model  = JobStatusHistory
    extra  = 0
    readonly_fields = ('old_status', 'new_status', 'changed_by', 'timestamp', 'comment')


class CommentInline(admin.TabularInline):
    model  = JobComment
    extra  = 0
    readonly_fields = ('author', 'timestamp')


class AttachmentInline(admin.TabularInline):
    model  = JobAttachment
    extra  = 0
    readonly_fields = ('uploaded_by', 'uploaded_at')


@admin.register(JobCard)
class JobCardAdmin(admin.ModelAdmin):
    list_display   = ('job_number', 'title', 'client', 'site', 'status',
                      'priority', 'due_date', 'date_assigned')
    list_filter    = ('status', 'priority', 'job_type', 'client')
    search_fields  = ('job_number', 'title', 'client__name')
    readonly_fields = ('job_number', 'date_assigned', 'created_at', 'updated_at')
    filter_horizontal = ('assigned_engineers',)
    inlines = [StatusHistoryInline, CommentInline, AttachmentInline]


@admin.register(JobStatusHistory)
class JobStatusHistoryAdmin(admin.ModelAdmin):
    list_display  = ('job_card', 'old_status', 'new_status', 'changed_by', 'timestamp')
    list_filter   = ('new_status',)
    search_fields = ('job_card__job_number',)


@admin.register(JobComment)
class JobCommentAdmin(admin.ModelAdmin):
    list_display  = ('job_card', 'author', 'timestamp')
    search_fields = ('job_card__job_number', 'text')


@admin.register(JobAttachment)
class JobAttachmentAdmin(admin.ModelAdmin):
    list_display  = ('job_card', 'file', 'uploaded_by', 'uploaded_at')
    search_fields = ('job_card__job_number',)
