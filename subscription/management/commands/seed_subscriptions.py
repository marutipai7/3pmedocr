from django.core.management.base import BaseCommand
from subscription.models import SubscriptionPlan, Feature

class Command(BaseCommand):
    help = "Seed subscription plans and features"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding subscription plans...")

        plans_data = [
            {
                "name": "Basic",
                "subtitle": "(Free)",
                "price": 0,
                "currency": "₹",
                "billing_cycle": "free",
                "button_text": "Subscribe",
                "display_order": 1,
                "features": [
                    ("Standard Company Dashboard", True),
                    ("📊 Activity Logs: Orders / discounts / stocks (Summary View)", True),
                    ("🧾 Pharma Metrics Reports (static and medicine analytics)", True),
                    ("📈 Platform Reports (Navigation, Coupons, Donations)", True),
                    ("📥 Downloaded Reports (PDF only)", False),
                    ("📬 Email Schedule Reports", False),
                    ("👥 24 Multi-user Team Access", False),
                    ("⚙️ Report Customization Tool", False),
                    ("📞 Priority Support", False),
                ],
            },
            {
                "name": "Standard Plan",
                "subtitle": "Incl. Quarterly 10% Disc",
                "price": 25000,
                "currency": "₹",
                "billing_cycle": "quarterly",
                "button_text": "Current Plan",
                "display_order": 2,
                "features": [
                    ("Custom Company Dashboard", True),
                    ("📊 Activity Logs: Standard and Save Reports.", True),
                    ("🧾 Pharma Metrics Reports: Standard and Save Reports.", True),
                    ("📈 Platform Reports: Standard and Save Reports", True),
                    ("📥 Download Reports. Detailed Filters & Export All Formats", True),
                    ("📬 Email Schedule Reports Monthly. Schedule and Auto send to recipients.", True),
                    ("👥 Multi-user Team Access: 3 Users/month", True),
                    ("⚙️ Report Customization Tool", False),
                    ("📞 Priority Support Email Only", False),
                ],
            },
            {
                "name": "Premium Plan",
                "subtitle": "Incl. Yearly 20% Disc",
                "price": 67500,
                "currency": "₹",
                "billing_cycle": "yearly",
                "button_text": "Subscribe",
                "display_order": 3,
                "features": [
                    ("Custom Company Dashboard", True),
                    ("📊 Activity Logs: Detailed Filters & Export, Custom Report Generator", True),
                    ("🧾 Pharma Metrics Reports: With custom Geo-filter & Date Range", True),
                    ("📈 Platform Reports: With custom Geo-filter & Date Range", True),
                    ("📥 Download Reports. Detailed Filters & Export All Formats", True),
                    ("📬 Email Schedule Reports Monthly. Schedule and Auto send to recipients.", True),
                    ("👥 Multi-user Team Access: 10 Users/month", True),
                    ("⚙️ Report Customization Tool Fully Custom, Visualize reports", True),
                    ("📞 Priority Support Email + Chat", True),
                ],
            },
            {
                "name": "Enterprise Plan",
                "subtitle": "(Custom)",
                "price": None,
                "currency": "₹",
                "billing_cycle": "custom",
                "is_custom_pricing": True,
                "button_text": "Contact Sales",
                "display_order": 4,
                "features": [
                    ("Custom Company Dashboard", True),
                    ("📊 Activity Logs: Detailed Filters & Export, Custom Report Generator, Realtime reports and heat maps.", True),
                    ("🧾 Pharma Metrics Reports: With custom Geo-filter & Date Range, Realtime reports and heat maps.", True),
                    ("📈 Platform Reports: With custom Geo-filter & Date Range, Realtime reports and heat maps.", True),
                    ("📥 Download Reports. Detailed Filters & Export All Formats + Custom API", True),
                    ("📬 Email Schedule Reports Custom period & Auto send to recipients.", True),
                    ("👥 Multi-user Team Access Customized Licenses count", True),
                    ("⚙️ Report Customization Tool Fully Custom, Visualize reports, Realtime reports and heat maps.", True),
                    ("📞 Priority Support Email + Chat + Phone", True),
                ],
            },
        ]

        for plan_data in plans_data:
            features = plan_data.pop("features", [])
            plan, created = SubscriptionPlan.objects.update_or_create(
                name=plan_data["name"],
                defaults=plan_data,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created plan: {plan.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated plan: {plan.name}"))

            # Clear old features & re-seed
            plan.features.all().delete()
            for idx, (text, included) in enumerate(features, start=1):
                Feature.objects.create(plan=plan, text=text, is_included=included, order=idx)

        self.stdout.write(self.style.SUCCESS("✅ Subscription plans and features seeded successfully"))
