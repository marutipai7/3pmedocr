from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = "Add location field and create 2dsphere index for all collections"

    def handle(self, *args, **kwargs):
        updated = 0
        for key, collection in settings.MONGO_COLLECTIONS.items():
            print(f"Processing {key}...")

            # Update documents without `location` field
            for doc in collection.find({"location": {"$exists": False}}):
                lat = doc.get("Latitude")
                lon = doc.get("Longitude")
                if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                    collection.update_one(
                        {"_id": doc["_id"]},
                        {"$set": {
                            "location": {
                                "type": "Point",
                                "coordinates": [lon, lat]
                            }
                        }}
                    )
                    updated += 1

            # Create index (if not already exists)
            collection.create_index([("location", "2dsphere")])
            print(f"{key}: Indexed & updated {updated} documents.\n")
        print("All done.")
