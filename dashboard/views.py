from django.shortcuts import render
from .models import SugarPrice
import json
from django.db import models
import time
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import random
from django.http import JsonResponse

@login_required
def market_trends(request):
    prices = SugarPrice.objects.all().order_by('date')

    if not prices.exists():
        # Return empty context if no data
        context = {
            'chart_data': json.dumps([]),
            'latest_price': 0,
            'exchange_rate': 0,
            'daily_change': 0,
            'daily_change_percent': 0,
            'annual_min': 0,
            'annual_max': 0,
            'volume': 0,
        }
        return render(request, 'dashboard/market_trends.html', context)

    # Prepare data for Highcharts Stock (timestamp in milliseconds)
    chart_data = []
    for price in prices:
        timestamp = int(time.mktime(price.date.timetuple())) * 1000
        chart_data.append([timestamp, float(price.amount)])

    # Key Metrics
    latest_price_obj = prices.last()
    if latest_price_obj and len(prices) > 1:
        latest_price = float(latest_price_obj.amount)
        exchange_rate = float(latest_price_obj.rate)
        
        # Get previous day's price for daily change calculation
        previous_price_obj = prices[len(prices)-2] if len(prices) > 1 else latest_price_obj
        previous_price = float(previous_price_obj.amount)
        
        daily_change = latest_price - previous_price
        daily_change_percent = (daily_change / previous_price) * 100 if previous_price > 0 else 0
        
        # Calculate annual range
        annual_range = prices.aggregate(
            min_price=models.Min('amount'), 
            max_price=models.Max('amount')
        )
        annual_min = float(annual_range['min_price']) if annual_range['min_price'] else 0
        annual_max = float(annual_range['max_price']) if annual_range['max_price'] else 0
        
        # Simulate trading volume (since we don't have real volume data)
        volume = random.randint(50000, 200000)
        
    else:
        latest_price = float(latest_price_obj.amount) if latest_price_obj else 0
        exchange_rate = float(latest_price_obj.rate) if latest_price_obj else 0
        daily_change = 0
        daily_change_percent = 0
        annual_min = latest_price
        annual_max = latest_price
        volume = 0

    context = {
        'chart_data': json.dumps(chart_data),
        'latest_price': latest_price,
        'exchange_rate': exchange_rate,
        'daily_change': daily_change,
        'daily_change_percent': daily_change_percent,
        'annual_min': annual_min,
        'annual_max': annual_max,
        'volume': volume,
    }
    return render(request, 'dashboard/market_trends.html', context)

def landing_chart_data(request):
    """
    Provides the last year of sugar price data for the landing page chart.
    """
    one_year_ago = datetime.now() - timedelta(days=365)
    prices = SugarPrice.objects.filter(date__gte=one_year_ago).order_by('date')
    
    chart_data = []
    for price in prices:
        timestamp = int(time.mktime(price.date.timetuple())) * 1000
        chart_data.append([timestamp, float(price.amount)])
        
    return JsonResponse(chart_data, safe=False)