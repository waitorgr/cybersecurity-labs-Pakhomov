# demoapp/management/commands/loaddemo.py
from django.core.management.base import BaseCommand
from demoapp.models import Person

class Command(BaseCommand):
    help = "Load demo persons"

    def handle(self, *args, **options):
        Person.objects.all().delete()
        demo = [
            ("John Doe", "john@example.com", "Loves pizza"),
            ("Jane Smith", "jane@example.com", "SSN: 123-45-6789"),
            ("Alice Admin", "alice@company.com", "Admin secret code: 42"),
            ("Bob User", "bob@example.com", "No secret"),
            ("Eve Hidden", "eve@hidden.com", "Hidden token: XYZ-999"),
        ]
        for name,email,secret in demo:
            Person.objects.create(name=name, email=email, secret_info=secret)
        self.stdout.write(self.style.SUCCESS("Demo data loaded"))
