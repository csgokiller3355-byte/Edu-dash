from django.core.management.base import BaseCommand
from home.models import User


class Command(BaseCommand):
    help = 'Delete all users except superusers, keeping admin accounts intact.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Get all superuser IDs to preserve
        superuser_ids = User.objects.filter(is_superuser=True).values_list('id', flat=True)
        superuser_count = superuser_ids.count()

        if superuser_count == 0:
            self.stdout.write(
                self.style.WARNING('No superusers found in the database. Aborting to prevent data loss.')
            )
            return

        self.stdout.write(f'Found {superuser_count} superuser(s) to preserve.')

        # Get all non-superuser users
        users_to_delete = User.objects.exclude(id__in=superuser_ids)
        delete_count = users_to_delete.count()

        if delete_count == 0:
            self.stdout.write(self.style.SUCCESS('No non-superuser users to delete. Database is already clean.'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run — no changes made.'))
            for user in users_to_delete:
                self.stdout.write(f'  Would delete: {user.username} (ID: {user.id}, email: {user.email})')
            self.stdout.write(f'\nTotal: {delete_count} user(s) would be deleted.')
            return

        # Delete all related objects first (CASCADE will handle FKs, but let's be explicit for logging)
        users_to_delete.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {delete_count} non-superuser user(s). '
                f'{superuser_count} superuser(s) preserved.'
            )
        )
