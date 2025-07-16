from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from .models import IssueType, IssueOption, SupportTicket
from dashboard.utils import dashboard_login_required
from django.core.exceptions import ValidationError
from rest_framework import serializers
from registration.models import User
from .models import ChatOptionGroup, CHATBOT_USER_TYPE_CHOICES
import logging
import json

logger = logging.getLogger(__name__) #for debugging purposes

@dashboard_login_required
@require_http_methods(["GET", "POST"])
def support_view(request):
    user = request.user_obj  # ✅ Make sure this is a real user
    issue_types = IssueType.objects.all()
    search_query = request.GET.get('search', '').strip()

    issue_types = IssueType.objects.exclude(name='chatbot_query').all()

    # 🔍 Ticket filtering — do NOT run this if user is anonymous
    tickets = SupportTicket.objects.filter(user_id=user.id).order_by('-created_at')

    if search_query:
        ticket_id_numeric = search_query.replace('#', '').strip()
        if ticket_id_numeric.isdigit():
            real_id = int(ticket_id_numeric) - 10000000
            tickets = tickets.filter(id=real_id)
        else:
            tickets = tickets.filter(
                Q(issue_option__name__icontains=search_query) |
                Q(issue_option__issue_type__name__icontains=search_query)
            )

    # 📨 Handle ticket submission
    if request.method == 'POST':
        issue_type_id = request.POST.get('issue_type')
        issue_option_id = request.POST.get('select_issue')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        if issue_type_id and issue_option_id:
            try:
                issue_option = IssueOption.objects.get(id=issue_option_id, issue_type_id=issue_type_id)
                ticket = SupportTicket.objects.create(
                    user=user,
                    created_by=user,
                    issue_option=issue_option,
                    description=description,
                    image=image
                )
                return JsonResponse({
                    'success': True,
                    'ticket_id': ticket.ticket_id(),
                    'message': 'Ticket created successfully.'
                })
            except IssueOption.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid issue type or option'}, status=400)

        return JsonResponse({'success': False, 'message': 'Missing issue type or option'}, status=400)

    return render(request, 'support.html', {
        'issue_types': issue_types,
        'tickets': tickets,
    })

# 🔄 AJAX: Load options for a given issue type (used in dropdown)
@dashboard_login_required
def get_issue_options(request):
    issue_type_id = request.GET.get('issue_type_id')
    print('Got issue_type_id:', issue_type_id)
    options = IssueOption.objects.filter(issue_type_id=issue_type_id)
    data = [{'id': opt.id, 'name': opt.name} for opt in options]
    return JsonResponse({'options': data})

# 🔍 Optional: Filter support tickets by status/issue type (if you use AJAX filtering)
@dashboard_login_required
def filter_support_tickets(request):
    status = request.GET.get('status')
    issue_type = request.GET.get('issue_type')
    tickets = SupportTicket.objects.all()

    if status:
        tickets = tickets.filter(status=status)
    if issue_type:
        tickets = tickets.filter(issue_option__issue_type__name=issue_type)

    data = serializers.serialize("json", tickets.select_related("issue_option", "user"))
    return JsonResponse({"tickets": data})


@dashboard_login_required
def submit_support_ticket(request):
    if request.method == "POST":
        issue_option_id = request.POST.get("select_issue")
        description = request.POST.get("description")
        image = request.FILES.get("image")

        try:
            issue_option = IssueOption.objects.get(id=issue_option_id)
        except IssueOption.DoesNotExist:
            return redirect("support_view") 

        SupportTicket.objects.create(
            user=request.user_obj,
            created_by=request.user_obj,
            issue_option=issue_option,
            description=description,
            image=image
        )
        return redirect("support_view")


# no use for now
@require_POST
@dashboard_login_required
def log_custom_query(request):
    user = request.user_obj
    try:
        data = json.loads(request.body)
        query_text = data.get('query')

        if not query_text:
            logger.warning("log_custom_query: Received request with no query text.")
            return JsonResponse({'message': 'Query text is required.'}, status=400)
        
        if not user:
             logger.error("log_custom_query: Unauthenticated user attempted to submit custom query.")
             return JsonResponse({'message': 'User not authenticated.'}, status=401)
        
        try:
            chatbot_issue_option = IssueOption.objects.get(
                issue_type__name='chatbot_query', 
                name='custome user query'         
            )
        except IssueOption.DoesNotExist:
            logger.error(
                "log_custom_query: Predefined 'chatbot_query - custom user query' "
                "IssueOption not found. Please ensure it exists in your database."
            )
            return JsonResponse(
                {'message': 'System error: Could not categorize query. Please contact direct support.'},
                status=500
            )
        except Exception as e:
            logger.error(f"log_custom_query: Error retrieving chatbot issue option: {e}", exc_info=True)
            return JsonResponse(
                {'message': 'An internal error occurred while setting up the ticket.'},
                status=500
            )
        
        ticket = SupportTicket.objects.create(
            user=user,
            created_by=user, 
            issue_option=chatbot_issue_option, 
            description=query_text, 
            image=None 
        )

        return JsonResponse({
            'success': True,
            'ticket_id': ticket.ticket_id(),
            'message': 'Your query has been submitted as a ticket! We will get back to you shortly.'
        }, status=200)
    
    except json.JSONDecodeError:
        logger.error("log_custom_query: Invalid JSON format in request body.")
        return JsonResponse({'message': 'Invalid data format.'}, status=400)
    
    except Exception as e:
        logger.exception(f"log_custom_query: An unexpected error occurred: {e}") 
        return JsonResponse({'message': 'An unexpected server error occurred. Please try again.'}, status=500)
    

@require_GET
@dashboard_login_required 
def get_user_tickets(request):
    try:
        user = request.user_obj
        user_tickets = SupportTicket.objects.filter(user=user).order_by('-created_at')

        tickets_data = []
        for ticket in user_tickets:
            tickets_data.append({
                'ticket_id': ticket.ticket_id(),
                'description': ticket.description,
                'status': ticket.status,
                'issue_option_name': ticket.issue_option.name if ticket.issue_option else 'N/A',
                'created_at': ticket.created_at.isoformat(), 
                # 'last_updated_at': ticket.created_at.isoformat(),
            })

        logger.info(f"Fetched {len(tickets_data)} tickets for user: {user.email}")
        return JsonResponse({'success': True, 'tickets': tickets_data}, safe=False, encoder=DjangoJSONEncoder)

    except Exception as e:
        logger.exception(f"Error fetching user tickets for {request.user.email if request.user.is_authenticated else 'unauthenticated user'}: {e}")
        return JsonResponse({'success': False, 'message': 'Failed to retrieve tickets.'}, status=500)


@require_GET
@dashboard_login_required 
def get_bot_content_api(request):
    user = request.user_obj
    user_type = 'user'
   
    if hasattr(user, 'ngoprofile') and user.ngoprofile is not None:
        user_type = 'ngo'
    elif hasattr(user, 'advertiserprofile') and user.advertiserprofile is not None:
        user_type = 'advertiser'
    elif hasattr(user, 'clientprofile') and user.clientprofile is not None:
        user_type = 'client'
    elif hasattr(user = 'medicalproviderprofile') and user.medicalproviderprofile is not None:
        user_type = 'provider'

    #logger.info(f"Chatbot content requested for user: {user.email}, determined type: {user_type}") #debugging

    try:
        chat_group = ChatOptionGroup.objects.get(user_type=user_type, is_active=True)
        return JsonResponse(chat_group.options_data)

    except ChatOptionGroup.DoesNotExist:
        logger.warning(f"No active ChatOptionGroup content found for user type: {user_type}. Falling back to 'user' content if available.")
        
        try:
            user_group = ChatOptionGroup.objects.get(user_type='user', is_active=True)
            fallback_data = user_group.options_data.copy()
            if user_type != 'user': 
                fallback_data["initial_message"] = f"No specific content found for your type ({user_type}). " + fallback_data.get("initial_message", "Here's some general information:")
            return JsonResponse(fallback_data, status=200) 

        except ChatOptionGroup.DoesNotExist:
            logger.error(f"No active ChatOptionGroup found for default 'user' type either. Chatbot content not configured.")
            return JsonResponse(
                {"initial_message": "Sorry, chatbot content is not configured. Please contact support."},
                status=500 
            )

    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching chatbot content for {user.email} ({user_type}): {e}", exc_info=True)
        return JsonResponse(
            {"initial_message": "Sorry, an unexpected error occurred. Please try again later."},
            status=500)

