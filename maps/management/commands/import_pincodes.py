# maps/management/commands/import_pincodes.py

import pandas as pd
from django.core.management.base import BaseCommand
from maps.models import PincodeLocation

class Command(BaseCommand):
    help = "Import valid pincode-lat-lon data with 5+ decimal precision"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", help="Path to the CSV file")

    def handle(self, *args, **options):
        df = pd.read_csv(options["csv_path"])
        objs = []
        dropped = []

        for index, row in df.iterrows():
            try:
                pincode_raw = row.get("pincode")
                lat = row.get("latitude")
                lon = row.get("longitude")

                # Validate lat/lon presence
                if pd.isnull(lat) or pd.isnull(lon):
                    raise ValueError("Missing lat/lon")

                # Force cast pincode to int first
                pincode_int = int(float(pincode_raw))
                pincode_str = str(pincode_int)

                if len(pincode_str) != 6:
                    raise ValueError(f"Invalid pincode: {pincode_str}")

                # Check decimal precision
                lat_dec = str(lat).split(".")[1] if "." in str(lat) else ""
                lon_dec = str(lon).split(".")[1] if "." in str(lon) else ""

                if len(lat_dec) < 5 or len(lon_dec) < 5:
                    continue
                objs.append(PincodeLocation(
                    pincode=pincode_str,
                    latitude=float(lat),
                    longitude=float(lon)
                ))

            except Exception as e:
                dropped.append((index, pincode_raw, lat, lon, str(e)))

        PincodeLocation.objects.bulk_create(objs, batch_size=500, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"✅ Imported {len(objs)} entries."))
