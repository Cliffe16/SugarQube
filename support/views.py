from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
import json
from .forms import SupportTicketForm

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