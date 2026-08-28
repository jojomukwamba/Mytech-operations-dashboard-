"""
Seed sample data: clients, sites, engineers, and a few job cards.
Usage:  python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from jobs.models import Client, Site, Engineer, JobCard, JobStatus, Priority, JobType


CLIENTS = [
    {'name': 'Zara Retail Solutions'},
    {'name': 'Apex Manufacturing Ltd'},
    {'name': 'GreenLeaf Logistics'},
]

SITES = [
    ('Zara Retail Solutions',  'Sandton HQ',       '123 Rivonia Rd, Sandton'),
    ('Zara Retail Solutions',  'Rosebank Branch',  '45 Oxford St, Rosebank'),
    ('Apex Manufacturing Ltd', 'Factory Floor A',  '7 Industrial Ave, Midrand'),
    ('GreenLeaf Logistics',    'Depot North',      '99 Truck Rd, Pretoria'),
]

ENGINEERS = [
    ('Sipho Dlamini',    'Network Engineer',   '071 000 0001', 'sipho@ftp.co.za', 'Networking'),
    ('Aisha Patel',      'CCTV Technician',    '072 000 0002', 'aisha@ftp.co.za', 'CCTV'),
    ('Marcus Thompson',  'Starlink Installer', '073 000 0003', 'marcus@ftp.co.za', 'Starlink'),
    ('Lerato Molefe',    'Cyber Analyst',      '074 000 0004', 'lerato@ftp.co.za', 'Cybersecurity'),
    ('Thabo Nkosi',      'Field Technician',   '075 000 0005', 'thabo@ftp.co.za', 'General'),
]


class Command(BaseCommand):
    help = 'Seed sample clients, sites, engineers, and job cards.'

    def handle(self, *args, **options):
        # ── Admin user ────────────────────────────────────────────────────────
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'is_superuser': True, 'is_staff': True, 'email': 'admin@ftp.co.za'},
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created admin user (admin / admin123)'))
        else:
            self.stdout.write('Admin user already exists.')

        # ── Clients ───────────────────────────────────────────────────────────
        clients = {}
        for cd in CLIENTS:
            c, _ = Client.objects.get_or_create(name=cd['name'])
            clients[c.name] = c
        self.stdout.write(self.style.SUCCESS(f'{len(clients)} clients ready.'))

        # ── Sites ─────────────────────────────────────────────────────────────
        for cname, sname, addr in SITES:
            Site.objects.get_or_create(
                client=clients[cname], site_name=sname,
                defaults={'address': addr},
            )
        self.stdout.write(self.style.SUCCESS(f'{len(SITES)} sites ready.'))

        # ── Engineers ─────────────────────────────────────────────────────────
        engineers = []
        for fname, role, phone, email, spec in ENGINEERS:
            e, _ = Engineer.objects.get_or_create(
                email=email,
                defaults={'full_name': fname, 'role': role, 'phone': phone,
                          'specialization': spec, 'active_status': True},
            )
            engineers.append(e)
        self.stdout.write(self.style.SUCCESS(f'{len(engineers)} engineers ready.'))

        # ── Job Cards ─────────────────────────────────────────────────────────
        sample_jobs = [
            {
                'client': clients['Zara Retail Solutions'],
                'site':   Site.objects.filter(site_name='Sandton HQ').first(),
                'title':  'CCTV System Installation',
                'job_type': JobType.CCTV,
                'status':   JobStatus.IN_PROGRESS,
                'priority': Priority.HIGH,
            },
            {
                'client': clients['Apex Manufacturing Ltd'],
                'site':   Site.objects.filter(site_name='Factory Floor A').first(),
                'title':  'Networking Upgrade – Floor A',
                'job_type': JobType.NETWORKING,
                'status':   JobStatus.ASSIGNED,
                'priority': Priority.MEDIUM,
            },
            {
                'client': clients['GreenLeaf Logistics'],
                'site':   Site.objects.filter(site_name='Depot North').first(),
                'title':  'Starlink Internet Setup',
                'job_type': JobType.STARLINK,
                'status':   JobStatus.COMPLETED,
                'priority': Priority.URGENT,
            },
        ]
        for jd in sample_jobs:
            if not jd['site']:
                continue
            exists = JobCard.objects.filter(title=jd['title'], client=jd['client']).exists()
            if not exists:
                JobCard.objects.create(
                    created_by=admin, last_updated_by=admin, **jd
                )
        self.stdout.write(self.style.SUCCESS('Sample job cards created.'))
        self.stdout.write(self.style.SUCCESS('\nSeed complete! Run the server and log in with admin / admin123'))
