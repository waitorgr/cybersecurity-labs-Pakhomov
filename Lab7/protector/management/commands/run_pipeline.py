from django.core.management.base import BaseCommand
from protector.models import FileRecord
from protector.pipeline import sign, encrypt, stego

class Command(BaseCommand):
    help = "Run pipeline for pending FileRecords"

    def handle(self, *args, **options):
        pending = FileRecord.objects.filter(container_image__isnull=True)
        for p in pending:
            self.stdout.write(f"Processing {p.id}")
            # тут можна викликати пайплайн функції напряму
