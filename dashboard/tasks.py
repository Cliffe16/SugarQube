from celery import shared_task
from .prediction_models import prepare_data, train_and_predict
from django.core.cache import cache
from .models import SugarPrice
from django.db import models
import json
import time

@shared_task
def update_market_trends(forecast_days):
    """
    A Celery task to update the market trends data and return the results.
    """
    historical_df = prepare_data()

    if historical_df.empty:
        return None

    predictions_df, accuracy_metrics, per_model_metrics = train_and_predict(
    historical_df,
    forecast_days=forecast_days
)

    # Format data for Highcharts
    chart_data = []
    for index, row in historical_df.iterrows():
        timestamp = int(time.mktime(index.timetuple())) * 1000
        chart_data.append([timestamp, float(row['Amount'])])

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
        'accuracy_metrics': accuracy_metrics,
        'forecast_days': forecast_days,
    }

    # Store the data in the cache
    cache_key = f'market_trends_{forecast_days}'
    cache.set(cache_key, context, 3600)
    
    return context


@shared_task
def prewarm_prediction_cache():
    """
    Pre-warm the prediction cache for common forecast periods.
    This should be run periodically (e.g., every 30 minutes) or after data updates.
    """
    from .prediction_models import prepare_data, train_and_predict
    import pandas as pd
    
    try:
        df = prepare_data()
        
        if df.empty or len(df) < 40:
            return {'status': 'no_data'}
        
        # Pre-calculate predictions for common forecast periods
        forecast_periods = [7, 14, 30]
        results = {}
        
        for days in forecast_periods:
            try:
                predictions_df, metrics = train_and_predict(df, forecast_days=days)
                
                # Format for API response
                preds_list = []
                for _, row in predictions_df.iterrows():
                    ts = int(pd.Timestamp(row['Date']).timestamp() * 1000)
                    val = float(row['Amount'])
                    preds_list.append([ts, val])
                
                response_data = {
                    'prediction': preds_list,
                    'metrics': metrics,
                    'forecast_days': days,
                    'model_hint': 'auto',
                    'ci': False
                }
                
                # Cache with the same key structure as api_predict
                cache_key = f'prediction_api_{days}_auto_False'
                cache.set(cache_key, response_data, 1800)  # 30 minutes
                
                results[f'{days}d'] = 'cached'
                
            except Exception as e:
                results[f'{days}d'] = f'error: {str(e)}'
        
        return {
            'status': 'success',
            'results': results,
            'timestamp': time.time()
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def update_on_price_change():
    """
    Trigger cache updates when new price data is added.
    Call this after bulk price imports or individual price updates.
    """
    # Clear old caches
    cache.delete('prepared_sugar_data')
    
    # Trigger pre-warming
    prewarm_prediction_cache.delay()
    
    # Update market trends for default period
    update_market_trends.delay(7)
    
    return {'status': 'caches_invalidated'}