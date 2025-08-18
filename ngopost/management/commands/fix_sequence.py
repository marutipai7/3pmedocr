from django.core.management.base import BaseCommand
from django.db import connection
from ngopost.models import NGOPost


class Command(BaseCommand):
    help = 'Fix the database sequence for NGOPost table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Get the current maximum ID
            cursor.execute("SELECT MAX(id) FROM ngopost_ngopost;")
            max_id = cursor.fetchone()[0]
            
            if max_id is None:
                self.stdout.write(self.style.SUCCESS('No records found in ngopost_ngopost table'))
                return
            
            # Reset the sequence to the next value after the maximum ID
            cursor.execute(
                "SELECT setval('ngopost_ngopost_id_seq', %s, true);",
                [max_id]
            )
            
            # Verify the sequence is set correctly
            cursor.execute("SELECT currval('ngopost_ngopost_id_seq');")
            current_seq = cursor.fetchone()[0]
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Sequence fixed! Max ID: {max_id}, Next sequence value: {current_seq + 1}'
                )
            ) 