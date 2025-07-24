from django.core.management.base import BaseCommand
from coupon.models import (
    CategoryOption, BrandOption, OfferTypeOption, CountryOption, StateOption, CityOption, PincodeOption, AgeOption, GenderOption, SpendingPowerOption
)

class Command(BaseCommand):
    help = 'Populate dropdown option tables for coupon app.'

    def handle(self, *args, **options):
        # Category
        categories = [
            'Food & Beverages', 'Grocery', 'Health & Wellness', 'Fitness & Gym', 'Clothing & Fashion',
            'Beauty & Salon', 'Electronics', 'Home Services', 'Transport & Travel', 'Education',
            'Entertainment & Events', 'Pharmacy & Medical', 'Other'
        ]
        for name in categories:
            CategoryOption.objects.get_or_create(name=name)

        # Brand
        brands = [
            'Starbucks', 'Dominos Pizza', 'Nike', 'Uber', 'Zomato', 'Apollo Pharmacy', 'Local Gym', '[Custom Brand Entry]'
        ]
        for name in brands:
            BrandOption.objects.get_or_create(name=name)

        # Offer Type
        offer_types = [
            'First Time User Discount', 'Fixed Amount', 'Free Trial', 'Percentage Discount'
        ]
        for name in offer_types:
            OfferTypeOption.objects.get_or_create(name=name)

        # Country
        countries = ['India', 'USA', 'Malaysia', 'Russia']
        for name in countries:
            CountryOption.objects.get_or_create(name=name)

        # State
        states = [
            ('Maharashtra', 'India'), ('Madhya Pradesh', 'India'), ('Andhra Pradesh', 'India'), ('Himachal Pradesh', 'India')
        ]
        for state_name, country_name in states:
            country, _ = CountryOption.objects.get_or_create(name=country_name)
            StateOption.objects.get_or_create(name=state_name, country=country)

        # City
        cities = [
            ('Pune', 'Maharashtra'), ('Nagpur', 'Maharashtra'), ('Mumbai', 'Maharashtra'), ('Nashik', 'Maharashtra')
        ]
        for city_name, state_name in cities:
            state = StateOption.objects.filter(name=state_name).first()
            if state:
                CityOption.objects.get_or_create(name=city_name, state=state)

        # Pincode
        pincodes = [
            ('480108', 'Pune'), ('473001', 'Nagpur'), ('473105', 'Mumbai'), ('473118', 'Nashik')
        ]
        for code, city_name in pincodes:
            city = CityOption.objects.filter(name=city_name).first()
            PincodeOption.objects.get_or_create(code=code, city=city)

        # Age
        ages = ['18-30 years', '31-50 years', '51+ years']
        for name in ages:
            AgeOption.objects.get_or_create(name=name)

        # Gender
        genders = ['Male', 'Female']
        for name in genders:
            GenderOption.objects.get_or_create(name=name)

        # Spending Power
        spending_powers = ['0-200 Per Month', '200-500 Per Month', '500 and Above Per Month']
        for name in spending_powers:
            SpendingPowerOption.objects.get_or_create(name=name)

        self.stdout.write(self.style.SUCCESS('Coupon dropdown options loaded successfully.')) 