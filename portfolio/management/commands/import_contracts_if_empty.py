"""
Safe boot helper: import contracts.csv only when the Project table is empty.
Does not overwrite an existing archive.
"""
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand

from portfolio.models import Project


class Command(BaseCommand):
    help = 'Import contracts.csv only if there are zero Project rows'

    def handle(self, *args, **options):
        count = Project.objects.count()
        if count > 0:
            self.stdout.write(self.style.NOTICE(
                f'Skip import_contracts_if_empty: {count} projects already present'
            ))
            return

        csv_path = Path(__file__).resolve().parents[3] / 'contracts.csv'
        if not csv_path.exists():
            self.stdout.write(self.style.WARNING(
                f'Skip import_contracts_if_empty: missing {csv_path}'
            ))
            return

        self.stdout.write(self.style.WARNING(
            f'Project table empty — importing once from {csv_path.name}'
        ))
        call_command('import_contracts', csv=str(csv_path))
        self.stdout.write(self.style.SUCCESS(
            f'Import finished: {Project.objects.count()} projects'
        ))
