import csv
from django.core.management.base import BaseCommand
from dashboard.models import SugarPrice
from datetime import datetime

class Command(BaseCommand):
    help = 'Efficiently bulk loads data from sugar prices CSV, skipping rows with errors.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Preparing for a new bulk import...")
        
        # 1. Clear existing data for a fresh start
        count, _ = SugarPrice.objects.using('sugarprices').all().delete()
        self.stdout.write(self.style.SUCCESS(f"Cleared {count} old price records."))

        file_path = 'dashboard/management/commands/sugarprices.csv'
        self.stdout.write(f"Reading and processing rows from {file_path}...")
        
        objects_to_create = []
        successful_reads = 0
        skipped_rows = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)  # Skip header

                for i, row in enumerate(reader, start=2):
                    try:
                        date_str, amount_str, rate_str = row
                        
                        if not all([date_str, amount_str, rate_str]):
                            self.stdout.write(self.style.WARNING(f"Skipping row {i}: missing data."))
                            skipped_rows += 1
                            continue
                        
                        # Create a SugarPrice object in memory (don't save yet)
                        price_obj = SugarPrice(
                            date=datetime.strptime(date_str.strip(), '%d/%m/%Y').date(),
                            amount=float(amount_str.strip()),
                            rate=float(rate_str.strip())
                        )
                        objects_to_create.append(price_obj)
                        successful_reads += 1

                    except (ValueError, IndexError) as e:
                        self.stdout.write(self.style.WARNING(f"Skipping row {i} due to formatting error: {e}"))
                        skipped_rows += 1
                        continue
            
            self.stdout.write(f"CSV processing complete. Found {successful_reads} valid records.")

            # 2. Perform the bulk insert
            if objects_to_create:
                self.stdout.write("Starting bulk import into the database...")
                SugarPrice.objects.using('sugarprices').bulk_create(objects_to_create, batch_size=1000)
                self.stdout.write(self.style.SUCCESS(f"\nImport complete!"))
                self.stdout.write(self.style.SUCCESS(f"Successfully imported {len(objects_to_create)} new records."))
            else:
                self.stdout.write(self.style.WARNING("No new records to import."))

            if skipped_rows > 0:
                self.stdout.write(self.style.WARNING(f"Skipped {skipped_rows} rows due to errors."))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Error: The file '{file_path}' was not found."))