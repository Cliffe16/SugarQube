from django.shortcuts import render
from .models import SugarPrice
import json
from django.db import models
import time
from django.contrib.auth.decorators import login_required # Import the decorator

@login_required # Add this decorator to secure the view
def market_trends(request):
    prices = SugarPrice.objects.all().order_by('date')

    # Prepare data for Highcharts Stock (timestamp in milliseconds)
    chart_data = [[int(time.mktime(price.date.timetuple())) * 1000, float(price.amount)] for price in prices]

    # Key Metrics
    latest_price_obj = prices.last()
    if latest_price_obj:
        latest_price = latest_price_obj.amount
        exchange_rate = latest_price_obj.rate
        daily_change = latest_price - prices[len(prices)-2].amount if len(prices) > 1 else 0
        annual_range = prices.aggregate(min_price=models.Min('amount'), max_price=models.Max('amount'))
        annual_min = annual_range['min_price']
        annual_max = annual_range['max_price']
    else:
        latest_price, exchange_rate, daily_change, annual_min, annual_max = 0, 0, 0, 0, 0


    context = {
        'chart_data': json.dumps(chart_data),
        'latest_price': latest_price,
        'exchange_rate': exchange_rate,
        'daily_change': daily_change,
        'annual_min': annual_min,
        'annual_max': annual_max,
    }
    return render(request, 'dashboard/market_trends.html', context)