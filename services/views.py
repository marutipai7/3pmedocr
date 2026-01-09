import json
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from dashboard.utils import dashboard_login_required, get_common_context
from .models import (
    LabRatePackage, 
    LabTestCategory, 
    LabTestPackageMaster, 
    LabModeType, 
    LabRegion, 
    LabDays, 
    LabRateMode
)
from settings.models import SellerSubscription

@dashboard_login_required
def services(request):
    user = request.user_obj
    context = get_common_context(request, user)

    if user.user_type == 'pharmacy':
        return render(request, 'pharmacy/services.html', context)
    elif user.user_type == 'lab':
        sub = SellerSubscription.objects.filter(
            seller_type="lab",
            seller_profile_id=user.lab_profile.id,
            is_active=True,
            is_enabled=True
        ).first()
        context["lab_categories"] = LabTestCategory.objects.all()
        context["lab_packages"] = LabTestPackageMaster.objects.select_related("category")
        context["lab_modes"] = LabModeType.objects.all()
        context["lab_regions"] = LabRegion.objects.all()
        context["lab_days"] = LabDays.objects.all()
        context["has_premium"] = bool(sub and not sub.is_expired)
        return render(request, 'lab/services.html', context)
    elif user.user_type == 'doctor':
        return render(request, 'doctor/services.html', context)
    elif user.user_type == 'hospital':
        return render(request, 'hospital/services.html', context)
    
@dashboard_login_required
def save_lab_services(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)

    services    = data.get("services", [])
    collections = data.get("collections", [])

    lab = request.user_obj.lab_profile

    saved_services    = []
    saved_collections = []

    for s in services:
        try:
            category = LabTestCategory.objects.get(id=s["category_id"])
            package  = LabTestPackageMaster.objects.get(id=s["package_id"])
        except (LabTestCategory.DoesNotExist, LabTestPackageMaster.DoesNotExist):
            continue

        day_obj = None
        if s.get("days"):
            try:
                day_obj = LabDays.objects.get(id=s["days"])
            except LabDays.DoesNotExist:
                pass

        obj = LabRatePackage.objects.create(
            lab=lab,
            category=category,
            package=package,
            days=day_obj,
            price=s.get("price") or 0
        )

        saved_services.append({
            "category_name": category.name,
            "package_name": package.name,
            "days_name": obj.days.name if obj.days else "",
            "price": str(obj.price)
        })

    for c in collections:
        try:
            mode = LabModeType.objects.get(id=c["mode_id"])
        except LabModeType.DoesNotExist:
            continue

        region = None
        if c.get("region_id"):
            try:
                region = LabRegion.objects.get(id=c["region_id"])
            except LabRegion.DoesNotExist:
                pass

        obj, created = LabRateMode.objects.update_or_create(
            lab=lab,
            mode_type=mode,
            region=region,
            defaults={
                "price": c.get("price") or 0,
                "is_active": True
            }
        )

        saved_collections.append({
            "mode_name": obj.mode_type.name,
            "region_name": obj.region.name if obj.region else None,
            "price": str(obj.price)
        })

    return JsonResponse({
        "success": True,
        "data": saved_services,
        "collection_data": saved_collections
    })


@dashboard_login_required
def get_lab_services(request):
    lab = request.user_obj.lab_profile

    # check premium
    sub = SellerSubscription.objects.filter(
        seller_type="lab",
        seller_profile_id=lab.id,
        is_active=True,
        is_enabled=True
    ).first()

    has_premium = bool(sub and not sub.is_expired)

    packages = LabRatePackage.objects.filter(lab=lab).select_related(
        "category", "package", "days"
    )

    test_packages = []
    for p in packages:
        test_packages.append({
            "category": p.category.name,
            "package": p.package.name,
            "days": p.days.name if p.days else "",
            "price": str(p.price)
        })

    modes = LabRateMode.objects.filter(lab=lab).select_related(
        "mode_type", "region"
    )

    collection_modes = []
    for m in modes:
        collection_modes.append({
            "mode": m.mode_type.name,
            "region": m.region.name if m.region else "",
            "price": str(m.price)
        })

    return JsonResponse({
        "success": True,
        "has_premium": has_premium,
        "test_packages": test_packages,
        "collection_modes": collection_modes
    })

