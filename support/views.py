from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
import json
from .forms import SupportTicketForm
from .models import SupportTicket

@csrf_exempt # Use exempt for simplicity in this context; for production, use standard CSRF tokens
@require_POST
def submit_ticket(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=401)
    
    try:
        data = json.loads(request.body)
        form = SupportTicketForm(data)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save() # .save() will generate the ticket_id

            # Send confirmation email
            subject = f"Support Ticket Created: #{ticket.ticket_id}"
            message = f"Hi {request.user.username},\n\nYour support ticket with the subject '{ticket.subject}' has been successfully created. Your ticket number is {ticket.ticket_id}.\n\nA support agent will get back to you shortly.\n\nThanks,\nSugarQube Support"
            
            send_mail(
                subject,
                message,
                'support@sugarqube.com',
                [request.user.email],
                fail_silently=False,
            )

            return JsonResponse({'success': 'Ticket created successfully!', 'ticket_id': ticket.ticket_id})
        else:
            return JsonResponse({'error': 'Invalid data', 'details': form.errors}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def support_page(request):
    """
    This view returns a list of all support tickets raised by a user
    """
    # Get sorting parameters from the URL
    sort_by = request.GET.get('sort', '-created_at')
    sort_dir = request.GET.get('dir', 'desc')

    # Whitelist of fields for sorting
    valid_sort_fields = ['ticket_id', 'created_at', 'subject', 'status']
    if sort_by not in valid_sort_fields:
        sort_by = 'created_at'  # Default sort

    # Determine sorting direction
    if sort_dir == 'desc':
        ordering = f'-{sort_by}'
        next_sort_dir = 'asc'
    else:
        ordering = sort_by
        next_sort_dir = 'desc'

    tickets = SupportTicket.objects.filter(user=request.user).order_by(ordering)

    context = {
        'tickets': tickets,
        'sort_by': sort_by,
        'sort_dir': sort_dir,
        'next_sort_dir': next_sort_dir,
    }
    return render(request, 'support/support_page.html', context)