from django.shortcuts import render
from .models import SugarPrice
import json
from django.db import models
import time
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .prediction_models import prepare_data, train_and_predict 
from django.http import JsonResponse


@login_required
def market_trends(request):
    historical_df = prepare_data()

    if historical_df.empty:
        return render(request, 'dashboard/market_trends.html', {'chart_data': json.dumps([])})

    # Get predictions and now also the accuracy metrics
    predictions_df, accuracy_metrics = train_and_predict(historical_df)

    # Format historical data for Highcharts
    chart_data = []
    for index, row in historical_df.iterrows():
        timestamp = int(time.mktime(row['Date'].timetuple())) * 1000
        chart_data.append([timestamp, float(row['Amount'])])
        
    # Format prediction data for Highcharts
    prediction_data = []
    for index, row in predictions_df.iterrows():
        timestamp = int(time.mktime(row['Date'].timetuple())) * 1000
        prediction_data.append([timestamp, float(row['Amount'])])

    # Calculate Key Metrics
    prices = SugarPrice.objects.all().order_by('date')
    latest_price_obj = prices.last()
    
    if latest_price_obj and prices.count() > 1:
        latest_price = float(latest_price_obj.amount)
        exchange_rate = float(latest_price_obj.rate)
        
        previous_price_obj = prices[prices.count()-2]
        previous_price = float(previous_price_obj.amount)
        
        daily_change = latest_price - previous_price
        daily_change_percent = (daily_change / previous_price) * 100 if previous_price > 0 else 0
        
        annual_range = prices.aggregate(min_price=models.Min('amount'), max_price=models.Max('amount'))
        annual_min = float(annual_range['min_price']) if annual_range['min_price'] else 0
        annual_max = float(annual_range['max_price']) if annual_range['max_price'] else 0
        
    else:
        latest_price = float(latest_price_obj.amount) if latest_price_obj else 0
        exchange_rate = float(latest_price_obj.rate) if latest_price_obj else 0
        daily_change = 0
        daily_change_percent = 0
        annual_min = latest_price
        annual_max = latest_price

    context = {
        'chart_data': json.dumps(chart_data),
        'prediction_data': json.dumps(prediction_data),
        'latest_price': latest_price,
        'EXCHANGE_RATE_USD': exchange_rate,
        'daily_change': daily_change,
        'daily_change_percent': daily_change_percent,
        'annual_min': annual_min,
        'annual_max': annual_max,
        'accuracy_metrics': accuracy_metrics, # Add accuracy metrics to the context
    }
    return render(request, 'dashboard/market_trends.html', context)

def landing_chart_data(request):
    """
    Provides sugar price data from the calendar year three years prior to the current year.
    """
    target_year = datetime.now().year - 5
    prices = SugarPrice.objects.filter(date__year=target_year).order_by('date')
    
    chart_data = []
    for price in prices:
        timestamp = int(time.mktime(price.date.timetuple())) * 1000
        chart_data.append([timestamp, float(price.amount)])
        
    return JsonResponse(chart_data, safe=False)