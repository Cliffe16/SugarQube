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
    forecast_days = int(request.GET.get('forecast_days', 7))
    cache_key = f'market_trends_{forecast_days}'
    cached_data = cache.get(cache_key)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Handle AJAX requests
        if cached_data:
            return JsonResponse(cached_data)
        else:
            task = update_market_trends.delay(forecast_days)
            return JsonResponse({'task_id': task.id})
    else:
        # Handle regular page loads
        if cached_data:
            return render(request, 'dashboard/market_trends.html', cached_data)
        else:
            task = update_market_trends.delay(forecast_days)
            return render(request, 'dashboard/market_trends.html', {'task_id': task.id})

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