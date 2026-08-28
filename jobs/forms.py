from django import forms
from .models import JobCard, JobComment, JobAttachment, Client, Site, TimeLog, Engineer


class ClientForm(forms.ModelForm):
    class Meta:
        model  = Client
        fields = ['name', 'phone_number', 'email']
        widgets = {
            'name':         forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email':        forms.EmailInput(attrs={'class': 'form-control'}),
        }


class EngineerForm(forms.ModelForm):
    class Meta:
        model  = Engineer
        fields = ['full_name', 'role', 'phone', 'email', 'specialization', 'active_status']
        widgets = {
            'full_name':      forms.TextInput(attrs={'class': 'form-control'}),
            'role':           forms.TextInput(attrs={'class': 'form-control'}),
            'phone':          forms.TextInput(attrs={'class': 'form-control'}),
            'email':          forms.EmailInput(attrs={'class': 'form-control'}),
            'specialization': forms.Select(attrs={'class': 'form-select'}),
            'active_status':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SiteForm(forms.ModelForm):
    class Meta:
        model  = Site
        fields = ['client', 'site_name', 'address']
        widgets = {
            'client':    forms.Select(attrs={'class': 'form-select'}),
            'site_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address':   forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }



class JobCardForm(forms.ModelForm):
    class Meta:
        model  = JobCard
        fields = [
            'title', 'description', 'client', 'site',
            'job_type', 'status', 'priority',
            'assigned_engineers', 'due_date',
            'device_sn', 'work_start_date',
            'risk_height', 'risk_confined_space', 'risk_dust_noise',
            'safety_ladder', 'safety_ppe', 'safety_mask', 'safety_harness'
        ]
        widgets = {
            'description':          forms.Textarea(attrs={'rows': 4}),
            'due_date':             forms.DateInput(attrs={'type': 'date'}),
            'work_start_date':      forms.DateInput(attrs={'type': 'date'}),
            'assigned_engineers':   forms.SelectMultiple(attrs={'size': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap classes
        for field_name, field in self.fields.items():
            widget = field.widget
            css = widget.attrs.get('class', '')
            if isinstance(widget, forms.SelectMultiple):
                widget.attrs['class'] = f'{css} form-select'.strip()
            elif isinstance(widget, (forms.Select,)):
                widget.attrs['class'] = f'{css} form-select'.strip()
            elif isinstance(widget, forms.Textarea):
                widget.attrs['class'] = f'{css} form-control'.strip()
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = f'{css} form-check-input'.strip()
            else:
                widget.attrs['class'] = f'{css} form-control'.strip()

        # Filter sites based on selected client (JS cascade also handles this)
        if 'client' in self.data:
            try:
                client_id = int(self.data.get('client'))
                self.fields['site'].queryset = Site.objects.filter(client_id=client_id)
            except (ValueError, TypeError):
                self.fields['site'].queryset = Site.objects.none()
        elif self.instance.pk and self.instance.client_id:
            self.fields['site'].queryset = Site.objects.filter(client=self.instance.client)
        else:
            self.fields['site'].queryset = Site.objects.all()


class CommentForm(forms.ModelForm):
    class Meta:
        model  = JobComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control',
                                          'placeholder': 'Add a comment…'}),
        }
        labels = {'text': ''}


class AttachmentForm(forms.ModelForm):
    class Meta:
        model  = JobAttachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class StatusChangeForm(forms.Form):
    new_status = forms.ChoiceField(
        choices=JobCard._meta.get_field('status').choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Optional comment…',
        }),
    )

class TimeLogForm(forms.ModelForm):
    class Meta:
        model = TimeLog
        fields = ['engineer', 'start_time', 'end_time']
        widgets = {
            'engineer': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
