from django.shortcuts import render
from dashboard.utils import dashboard_login_required, get_common_context
import os
import tempfile
from django.http import JsonResponse
from .utils import process_document

@dashboard_login_required
def shared(request):
    user = request.user_obj
    context = get_common_context(request, user)
    return render(request, 'share.html', context)

@dashboard_login_required
def ocr_upload(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp_file:
            for chunk in file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name

        result = process_document(tmp_path)
        os.remove(tmp_path)

        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@dashboard_login_required
def database_upload(request):
    pass

@dashboard_login_required
def save_bills(request):
    pass

@dashboard_login_required
def save_prescriptions(request):
    pass