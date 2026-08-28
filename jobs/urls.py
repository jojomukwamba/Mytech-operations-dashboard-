from django.urls import path
from . import views

urlpatterns = [
    path('',                         views.dashboard,          name='dashboard'),
    path('jobs/',                    views.job_list,           name='job_list'),
    path('jobs/new/',                views.job_create,         name='job_create'),
    path('jobs/<int:pk>/',           views.job_detail,         name='job_detail'),
    path('jobs/<int:pk>/print/',     views.job_print,          name='job_print'),
    path('jobs/<int:pk>/edit/',      views.job_edit,           name='job_edit'),
    path('engineers/workload/',      views.engineer_workload,  name='engineer_workload'),

    # Client CRUD
    path('clients/',                 views.client_list,        name='client_list'),
    path('clients/new/',             views.client_create,      name='client_create'),
    path('clients/<int:pk>/edit/',   views.client_edit,        name='client_edit'),
    path('clients/<int:pk>/delete/', views.client_delete,      name='client_delete'),

    # Engineer CRUD
    path('engineers/',               views.engineer_list,      name='engineer_list'),
    path('engineers/new/',           views.engineer_create,    name='engineer_create'),
    path('engineers/<int:pk>/edit/', views.engineer_edit,      name='engineer_edit'),
    path('engineers/<int:pk>/delete/', views.engineer_delete,  name='engineer_delete'),

    # Site CRUD
    path('sites/',                   views.site_list,          name='site_list'),
    path('sites/new/',               views.site_create,        name='site_create'),
    path('sites/<int:pk>/edit/',     views.site_edit,          name='site_edit'),
    path('sites/<int:pk>/delete/',   views.site_delete,        name='site_delete'),

    # APIs
    path('api/sites/',               views.api_sites_for_client, name='api_sites'),
    path('api/jobs/<int:pk>/status/', views.api_update_status,  name='api_update_status'),
]

