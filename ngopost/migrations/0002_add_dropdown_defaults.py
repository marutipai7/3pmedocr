from django.db import migrations

def add_dropdown_data(apps, schema_editor):
    PostTypeOption = apps.get_model('ngopost', 'PostTypeOption')
    DonationFrequencyOption = apps.get_model('ngopost', 'DonationFrequencyOption')
    CountryOption = apps.get_model('ngopost', 'CountryOption')
    StateOption = apps.get_model('ngopost', 'StateOption')
    CityOption = apps.get_model('ngopost', 'CityOption')
    AgeOption = apps.get_model('ngopost', 'AgeOption')
    GenderOption = apps.get_model('ngopost', 'GenderOption')
    SpendingPowerOption = apps.get_model('ngopost', 'SpendingPowerOption')

    # Post Types
    for name in ['Education', 'Health', 'Food']:
        PostTypeOption.objects.get_or_create(name=name)

    # Donation Frequencies
    for name in ['One-time', 'Monthly', 'Yearly']:
        DonationFrequencyOption.objects.get_or_create(name=name)

    # Countries
    india, _ = CountryOption.objects.get_or_create(name='India')
    usa, _ = CountryOption.objects.get_or_create(name='USA')

    # States
    maharashtra, _ = StateOption.objects.get_or_create(name='Maharashtra', country=india)
    karnataka, _ = StateOption.objects.get_or_create(name='Karnataka', country=india)

    # Cities
    CityOption.objects.get_or_create(name='Pune', state=maharashtra)
    CityOption.objects.get_or_create(name='Mumbai', state=maharashtra)
    CityOption.objects.get_or_create(name='Bangalore', state=karnataka)

    # Age
    for name in ['Children', 'Adults', 'Seniors']:
        AgeOption.objects.get_or_create(name=name)

    # Gender
    for name in ['Male', 'Female', 'Other']:
        GenderOption.objects.get_or_create(name=name)

    # Spending Power
    for name in ['Low', 'Medium', 'High']:
        SpendingPowerOption.objects.get_or_create(name=name)

class Migration(migrations.Migration):

    dependencies = [
        ('ngopost', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_dropdown_data),
    ] 