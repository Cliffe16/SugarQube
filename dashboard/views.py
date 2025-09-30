from django.shortcuts import render
from .models import SugarPrice
import time
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.http import JsonResponse
from django.core.cache import cache
from .tasks import update_market_trends
from celery.result import AsyncResult

@login_required
def market_trends(request):
    """
    Handles both cached and non-cached requests for market trends.
    """
    forecast_days = int(request.GET.get('forecast_days', 7))
    cache_key = f'market_trends_{forecast_days}'
    
    # Try to get the data from the cache
    context = cache.get(cache_key)

    # If the data is not in the cache, generate it now
    if context is None:
        # Call the task's logic directly (synchronously) to get the data
        # for the initial page load.
        context = update_market_trends(forecast_days)

    # If the task returned no data (e.g., empty database), provide an empty context
    # to prevent the template from breaking.
    if context is None:
        context = {}

    # Always render the page with a context that the template can use
    return render(request, 'dashboard/market_trends.html', context)

def task_status(request, task_id):
    task = AsyncResult(task_id)
    if task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'result': task.result,
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'status': str(task.info),
        }
    else:
        response = {
            'state': task.state,
        }
    return JsonResponse(response)

def landing_chart_data(request):
    target_year = datetime.now().year - 5
    prices = SugarPrice.objects.filter(date__year=target_year).order_by('date')
    chart_data = [[int(time.mktime(p.date.timetuple())) * 1000, float(p.amount)] for p in prices]
    return JsonResponse(chart_data, safe=False)