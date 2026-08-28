import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import (
    JobCard, JobStatus, Priority, Engineer, Client, Site,
    JobStatusHistory, JobComment, JobAttachment, TimeLog,
)
from .forms import (
    JobCardForm, CommentForm, AttachmentForm, StatusChangeForm, TimeLogForm,
    ClientForm, EngineerForm, SiteForm,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _dashboard_counts():
    today = datetime.date.today()
    closed_statuses = [JobStatus.COMPLETED, JobStatus.REVIEWED_CLOSED]
    open_jobs    = JobCard.objects.exclude(status__in=closed_statuses)
    overdue_jobs = open_jobs.filter(due_date__lt=today)
    by_status    = {s: JobCard.objects.filter(status=s).count()
                    for s, _ in JobStatus.choices}
    by_priority  = {p: JobCard.objects.filter(priority=p).count()
                    for p, _ in Priority.choices}
    return {
        'total_open':   open_jobs.count(),
        'overdue':      overdue_jobs.count(),
        'by_status':    by_status,
        'by_priority':  by_priority,
    }


# ── Dashboard ──────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    counts  = _dashboard_counts()
    columns = {}
    for status, label in JobStatus.choices:
        columns[label] = JobCard.objects.filter(status=status).select_related('client', 'site')
    context = {
        'counts':           counts,
        'columns':          columns,
        'statuses':         JobStatus.choices,
        'priority_choices': Priority.choices,
    }
    return render(request, 'jobs/dashboard.html', context)


# ── Job List ───────────────────────────────────────────────────────────────────

@login_required
def job_list(request):
    qs = JobCard.objects.select_related('client', 'site').prefetch_related('assigned_engineers')
    today = datetime.date.today()

    # ── filters ──
    q         = request.GET.get('q', '').strip()
    status    = request.GET.get('status', '')
    priority  = request.GET.get('priority', '')
    engineer  = request.GET.get('engineer', '')
    client    = request.GET.get('client', '')
    date_from = request.GET.get('date_from', '')
    date_to   = request.GET.get('date_to', '')
    sort      = request.GET.get('sort', '-created_at')

    if q:
        qs = qs.filter(Q(job_number__icontains=q) | Q(title__icontains=q))
    if status:
        qs = qs.filter(status=status)
    if priority:
        qs = qs.filter(priority=priority)
    if engineer:
        qs = qs.filter(assigned_engineers__id=engineer)
    if client:
        qs = qs.filter(client__id=client)
    if date_from:
        qs = qs.filter(date_assigned__date__gte=date_from)
    if date_to:
        qs = qs.filter(date_assigned__date__lte=date_to)

    allowed_sorts = ['job_number', '-job_number', 'title', '-title',
                     'due_date', '-due_date', 'priority', '-priority',
                     'status', '-status', 'created_at', '-created_at']
    if sort in allowed_sorts:
        qs = qs.order_by(sort)

    context = {
        'jobs':         qs,
        'engineers':    Engineer.objects.filter(active_status=True),
        'clients':      Client.objects.all(),
        'statuses':     JobStatus.choices,
        'priorities':   Priority.choices,
        'today':        today,
        'filters': {
            'q': q, 'status': status, 'priority': priority,
            'engineer': engineer, 'client': client,
            'date_from': date_from, 'date_to': date_to, 'sort': sort,
        },
    }
    return render(request, 'jobs/job_list.html', context)


# ── Job Detail ─────────────────────────────────────────────────────────────────

@login_required
def job_detail(request, pk):
    job            = get_object_or_404(JobCard, pk=pk)
    comment_form   = CommentForm()
    attachment_form = AttachmentForm()
    status_form    = StatusChangeForm(initial={'new_status': job.status})
    time_log_form  = TimeLogForm()
    # pre-fill engineer options to only those assigned to the job if applicable
    if job.assigned_engineers.exists():
        time_log_form.fields['engineer'].queryset = job.assigned_engineers.all()

    today          = datetime.date.today()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'comment':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                c = comment_form.save(commit=False)
                c.job_card = job
                c.author   = request.user
                c.save()
                messages.success(request, 'Comment added.')
                return redirect('job_detail', pk=pk)

        elif action == 'attach':
            attachment_form = AttachmentForm(request.POST, request.FILES)
            if attachment_form.is_valid():
                a = attachment_form.save(commit=False)
                a.job_card    = job
                a.uploaded_by = request.user
                a.save()
                messages.success(request, 'File attached.')
                return redirect('job_detail', pk=pk)

        elif action == 'time_log':
            time_log_form = TimeLogForm(request.POST)
            if time_log_form.is_valid():
                tl = time_log_form.save(commit=False)
                tl.job_card = job
                tl.save()
                messages.success(request, 'Time log added.')
                return redirect('job_detail', pk=pk)

        elif action == 'status':
            status_form = StatusChangeForm(request.POST)
            if status_form.is_valid():
                new_status = status_form.cleaned_data['new_status']
                comment    = status_form.cleaned_data.get('comment', '')
                if new_status != job.status:
                    old_status         = job.status
                    job.status         = new_status
                    job.last_updated_by = request.user
                    if new_status == JobStatus.COMPLETED:
                        job.date_completed = today
                    job.save()
                    # Patch in the comment on the auto-created history entry
                    last_hist = job.status_history.last()
                    if last_hist and comment:
                        last_hist.comment = comment
                        last_hist.save()
                    messages.success(request, f'Status changed to {new_status}.')
                return redirect('job_detail', pk=pk)

    context = {
        'job':             job,
        'comment_form':    comment_form,
        'attachment_form': attachment_form,
        'status_form':     status_form,
        'time_log_form':   time_log_form,
        'history':         job.status_history.all(),
        'comments':        job.comments.all(),
        'attachments':     job.attachments.all(),
        'time_logs':       job.time_logs.all(),
        'today':           today,
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def job_print(request, pk):
    job = get_object_or_404(JobCard, pk=pk)
    context = {
        'job': job,
        'time_logs': job.time_logs.all(),
    }
    return render(request, 'jobs/job_print.html', context)


# ── Job Create / Edit ──────────────────────────────────────────────────────────

def _resolve_inline_records(request, post_data, form):
    """
    Check for inline new client / site / engineer fields submitted alongside
    the job form. Create records that don't exist yet and patch the POST data
    so the form validation uses the correct IDs.
    Returns (patched_post, new_engineer_obj_or_None, error_message_or_None)
    """
    post = post_data.copy()
    new_engineer = None
    error = None

    # ── Inline Client ────────────────────────────────────────────────────────
    new_client_name  = post.get('new_client_name', '').strip()
    new_client_phone = post.get('new_client_phone', '').strip()
    new_client_email = post.get('new_client_email', '').strip()

    if new_client_name and not post.get('client'):
        client, created = Client.objects.get_or_create(
            name=new_client_name,
            defaults={'phone_number': new_client_phone, 'email': new_client_email},
        )
        if created:
            messages.info(request, f'Client "{client.name}" created.')
        post['client'] = str(client.pk)

    # ── Inline Site ──────────────────────────────────────────────────────────
    new_site_name    = post.get('new_site_name', '').strip()
    new_site_address = post.get('new_site_address', '').strip()

    if new_site_name and not post.get('site'):
        client_id = post.get('client', '')
        if client_id:
            try:
                client_obj = Client.objects.get(pk=int(client_id))
                site, created = Site.objects.get_or_create(
                    client=client_obj,
                    site_name=new_site_name,
                    defaults={'address': new_site_address},
                )
                if created:
                    messages.info(request, f'Site "{site.site_name}" created.')
                post['site'] = str(site.pk)
            except (Client.DoesNotExist, ValueError):
                error = 'Please select or create a valid client before adding a new site.'
        else:
            error = 'Please select or create a client before adding a new site.'

    # ── Inline Engineer ──────────────────────────────────────────────────────
    new_eng_name  = post.get('new_engineer_name', '').strip()
    new_eng_phone = post.get('new_engineer_phone', '').strip()

    if new_eng_name:
        new_engineer, created = Engineer.objects.get_or_create(
            full_name=new_eng_name,
            defaults={'phone': new_eng_phone, 'role': 'Engineer'},
        )
        if created:
            messages.info(request, f'Engineer "{new_engineer.full_name}" added.')

    return post, new_engineer, error


@login_required
def job_create(request):
    if request.method == 'POST':
        patched_post, new_engineer, inline_error = _resolve_inline_records(request, request.POST, None)
        form = JobCardForm(patched_post)
        if inline_error:
            messages.error(request, inline_error)
        elif form.is_valid():
            job = form.save(commit=False)
            job.created_by      = request.user
            job.last_updated_by = request.user
            job.save()
            form.save_m2m()
            if new_engineer:
                job.assigned_engineers.add(new_engineer)
            messages.success(request, f'Job {job.job_number} created.')
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobCardForm()
    return render(request, 'jobs/job_form.html', {'form': form, 'action': 'Create'})


@login_required
def job_edit(request, pk):
    job = get_object_or_404(JobCard, pk=pk)
    if request.method == 'POST':
        patched_post, new_engineer, inline_error = _resolve_inline_records(request, request.POST, None)
        form = JobCardForm(patched_post, instance=job)
        if inline_error:
            messages.error(request, inline_error)
        elif form.is_valid():
            j = form.save(commit=False)
            j.last_updated_by = request.user
            j.save()
            form.save_m2m()
            if new_engineer:
                job.assigned_engineers.add(new_engineer)
            messages.success(request, f'Job {job.job_number} updated.')
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobCardForm(instance=job)
    return render(request, 'jobs/job_form.html', {'form': form, 'action': 'Edit', 'job': job})


# ── Engineer Workload ──────────────────────────────────────────────────────────

@login_required
def engineer_workload(request):
    engineers = Engineer.objects.filter(active_status=True).prefetch_related('job_cards')
    data = []
    for eng in engineers:
        jobs = eng.job_cards.all()
        row  = {'engineer': eng, 'total': jobs.count()}
        for status, label in JobStatus.choices:
            row[status.replace(' ', '_').replace('/', '_')] = jobs.filter(status=status).count()
        data.append(row)
    context = {
        'data':     data,
        'statuses': JobStatus.choices,
    }
    return render(request, 'jobs/engineer_workload.html', context)


# ── API: sites for a client (cascade dropdown) ─────────────────────────────────

@login_required
def api_sites_for_client(request):
    client_id = request.GET.get('client_id')
    if client_id:
        sites = Site.objects.filter(client_id=client_id).values('id', 'site_name')
    else:
        sites = []
    return JsonResponse({'sites': list(sites)})


# ── API: update job status (Kanban drag-and-drop) ─────────────────────────────

@require_POST
@login_required
def api_update_status(request, pk):
    import json
    job = get_object_or_404(JobCard, pk=pk)
    try:
        body       = json.loads(request.body)
        new_status = body.get('status', '')
    except (ValueError, KeyError):
        return JsonResponse({'error': 'Invalid payload'}, status=400)

    valid = [s for s, _ in JobStatus.choices]
    if new_status not in valid:
        return JsonResponse({'error': 'Invalid status'}, status=400)

    job.status          = new_status
    job.last_updated_by = request.user
    if new_status == JobStatus.COMPLETED:
        job.date_completed = datetime.date.today()
    job.save()
    return JsonResponse({'ok': True, 'job_number': job.job_number, 'status': job.status})


# ── Client CRUD ────────────────────────────────────────────────────────────────

@login_required
def client_list(request):
    clients = Client.objects.annotate(site_count=Count('sites'), job_count=Count('jobs'))
    return render(request, 'jobs/client_list.html', {'clients': clients})


@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Client "{form.instance.name}" created.')
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'jobs/client_form.html', {'form': form, 'action': 'Add'})


@login_required
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f'Client "{client.name}" updated.')
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'jobs/client_form.html', {'form': form, 'action': 'Edit', 'client': client})


@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        name = client.name
        client.delete()
        messages.success(request, f'Client "{name}" deleted.')
        return redirect('client_list')
    return render(request, 'jobs/confirm_delete.html', {'object': client, 'type': 'Client', 'back_url': 'client_list'})


# ── Engineer CRUD ──────────────────────────────────────────────────────────────

@login_required
def engineer_list(request):
    engineers = Engineer.objects.annotate(job_count=Count('job_cards'))
    return render(request, 'jobs/engineer_list.html', {'engineers': engineers})


@login_required
def engineer_create(request):
    if request.method == 'POST':
        form = EngineerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Engineer "{form.instance.full_name}" added.')
            return redirect('engineer_list')
    else:
        form = EngineerForm()
    return render(request, 'jobs/engineer_form.html', {'form': form, 'action': 'Add'})


@login_required
def engineer_edit(request, pk):
    engineer = get_object_or_404(Engineer, pk=pk)
    if request.method == 'POST':
        form = EngineerForm(request.POST, instance=engineer)
        if form.is_valid():
            form.save()
            messages.success(request, f'Engineer "{engineer.full_name}" updated.')
            return redirect('engineer_list')
    else:
        form = EngineerForm(instance=engineer)
    return render(request, 'jobs/engineer_form.html', {'form': form, 'action': 'Edit', 'engineer': engineer})


@login_required
def engineer_delete(request, pk):
    engineer = get_object_or_404(Engineer, pk=pk)
    if request.method == 'POST':
        name = engineer.full_name
        engineer.delete()
        messages.success(request, f'Engineer "{name}" deleted.')
        return redirect('engineer_list')
    return render(request, 'jobs/confirm_delete.html', {'object': engineer, 'type': 'Engineer', 'back_url': 'engineer_list'})


# ── Site CRUD ──────────────────────────────────────────────────────────────────

@login_required
def site_list(request):
    sites = Site.objects.select_related('client').annotate(job_count=Count('jobs'))
    return render(request, 'jobs/site_list.html', {'sites': sites})


@login_required
def site_create(request):
    if request.method == 'POST':
        form = SiteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Site "{form.instance.site_name}" created.')
            return redirect('site_list')
    else:
        form = SiteForm()
    return render(request, 'jobs/site_form.html', {'form': form, 'action': 'Add'})


@login_required
def site_edit(request, pk):
    site = get_object_or_404(Site, pk=pk)
    if request.method == 'POST':
        form = SiteForm(request.POST, instance=site)
        if form.is_valid():
            form.save()
            messages.success(request, f'Site "{site.site_name}" updated.')
            return redirect('site_list')
    else:
        form = SiteForm(instance=site)
    return render(request, 'jobs/site_form.html', {'form': form, 'action': 'Edit', 'site': site})


@login_required
def site_delete(request, pk):
    site = get_object_or_404(Site, pk=pk)
    if request.method == 'POST':
        name = site.site_name
        site.delete()
        messages.success(request, f'Site "{name}" deleted.')
        return redirect('site_list')
    return render(request, 'jobs/confirm_delete.html', {'object': site, 'type': 'Site', 'back_url': 'site_list'})

