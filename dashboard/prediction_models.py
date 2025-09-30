import pandas as pd
from .models import SugarPrice
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import numpy as np
from sklearn.metrics import mean_absolute_error, r2_score, mean_absolute_percentage_error
from sklearn.preprocessing import StandardScaler
import warnings
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import hashlib
import json

warnings.filterwarnings("ignore")

def prepare_data():
    """
    Prepares data for model training with enhanced cleaning.
    Uses caching to avoid repeated database queries.
    """
    cache_key = 'prepared_sugar_data'
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        return pd.read_json(cached_data, orient='split')
    
    prices = SugarPrice.objects.all().values('date', 'amount')
    df = pd.DataFrame(list(prices))

    if df.empty:
        return df

    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    df = df.rename(columns={'amount': 'Amount'})
    df.index.name = 'Date'
    df = df.sort_index()
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    
    # Remove any NaN values
    df = df.dropna()
    
    # Remove duplicates, keeping the last entry for each date
    df = df[~df.index.duplicated(keep='last')]
    
    # Remove extreme outliers (beyond 3 standard deviations)
    mean_val = df['Amount'].mean()
    std_val = df['Amount'].std()
    df = df[np.abs(df['Amount'] - mean_val) <= (3 * std_val)]
    
    # Cache for 30 minutes
    cache.set(cache_key, df.to_json(orient='split'), 1800)
    
    return df

def create_features(df):
    """
    Creates additional features that might improve predictions.
    """
    df = df.copy()
    
    # Rolling statistics
    df['MA7'] = df['Amount'].rolling(window=7, min_periods=1).mean()
    df['MA30'] = df['Amount'].rolling(window=30, min_periods=1).mean()
    df['STD7'] = df['Amount'].rolling(window=7, min_periods=1).std()
    
    # Lag features
    df['Lag1'] = df['Amount'].shift(1)
    df['Lag7'] = df['Amount'].shift(7)
    
    # Rate of change
    df['ROC'] = df['Amount'].pct_change()
    
    # Fill NaN values created by rolling/shifting
    df = df.fillna(method='bfill')
    
    return df

def walk_forward_validation(data, order, n_test=30):
    """
    Performs walk-forward validation to get more realistic predictions.
    """
    predictions = []
    actuals = []
    
    train_size = len(data) - n_test
    
    for i in range(n_test):
        train = data[:train_size + i]
        test_value = data.iloc[train_size + i]
        
        try:
            model = ARIMA(train, order=order)
            model_fit = model.fit()
            pred = model_fit.forecast(steps=1)[0]
            predictions.append(pred)
            actuals.append(test_value)
        except:
            # If model fails, use last value
            predictions.append(train.iloc[-1])
            actuals.append(test_value)
    
    return np.array(predictions), np.array(actuals)

def find_best_model(data, test_size=30):
    """
    Tries multiple approaches and returns the best one based on validation.
    Caches the result to avoid repeated computation.
    """
    # Create a cache key based on data characteristics
    data_hash = hashlib.md5(str(data.values[-100:]).encode()).hexdigest()
    cache_key = f'best_model_{data_hash}_{test_size}'
    cached_result = cache.get(cache_key)
    
    if cached_result is not None:
        return cached_result
    
    if len(data) < test_size + 20:
        return None, None, float('inf')
    
    train_data = data[:-test_size]
    test_data = data[-test_size:]
    
    best_mae = float('inf')
    best_config = None
    best_type = None
    
    # Test different ARIMA configurations
    configs = [
        (0, 1, 1),  # Simple integrated MA
        (1, 1, 0),  # Simple integrated AR
        (1, 1, 1),  # Standard ARIMA
        (2, 1, 1),  # More AR terms
        (1, 1, 2),  # More MA terms
        (2, 1, 2),  # Balanced
        (0, 1, 0),  # Random walk
        (1, 0, 1),  # No differencing
    ]
    
    for order in configs:
        try:
            # Use walk-forward validation for this configuration
            preds, acts = walk_forward_validation(data, order, test_size)
            mae = mean_absolute_error(acts, preds)
            
            if mae < best_mae:
                best_mae = mae
                best_config = order
                best_type = 'ARIMA'
        except:
            continue
    
    # Test Exponential Smoothing
    try:
        model = ExponentialSmoothing(train_data, trend='add', seasonal=None, damped_trend=True)
        fit = model.fit()
        exp_pred = fit.forecast(steps=test_size)
        exp_mae = mean_absolute_error(test_data, exp_pred)
        
        if exp_mae < best_mae:
            best_mae = exp_mae
            best_config = 'exp_smoothing'
            best_type = 'ETS'
    except:
        pass
    
    # Test simple baseline (moving average)
    window = min(7, len(train_data) // 2)
    baseline_pred = np.full(test_size, train_data[-window:].mean())
    baseline_mae = mean_absolute_error(test_data, baseline_pred)
    
    if baseline_mae < best_mae:
        best_mae = baseline_mae
        best_config = window
        best_type = 'MA'
    
    result = (best_type, best_config, best_mae)
    
    # Cache for 1 hour
    cache.set(cache_key, result, 3600)
    
    return result

def train_and_predict(df, forecast_days=14):
    """
    Main function that orchestrates the prediction process with improved accuracy.
    
    Args:
        df: DataFrame with historical price data
        forecast_days: Number of days to forecast (default: 14, recommended: 7-14)
    """
    if df.empty or len(df) < 40:
        return pd.DataFrame(), {'mae': 0, 'r2': 0, 'mape': 0}
    
    # Validate forecast_days
    forecast_days = max(1, min(forecast_days, 30))  # Cap between 1-30 days
    
    data = df['Amount'].copy()
    
    # Find the best model using validation
    test_size = min(30, len(data) // 4)
    best_type, best_config, validation_mae = find_best_model(data, test_size)
    
    # Split for final evaluation
    train_data = data[:-test_size]
    test_data = data[-test_size:]
    
    # Train and predict based on best model
    if best_type == 'ARIMA':
        try:
            # Use walk-forward for test predictions (more accurate)
            test_predictions, _ = walk_forward_validation(data, best_config, test_size)
            
            # Train on full data for future predictions
            full_model = ARIMA(data, order=best_config)
            full_fit = full_model.fit()
            future_forecast = full_fit.forecast(steps=forecast_days)
            
        except Exception as e:
            print(f"ARIMA failed: {e}")
            # Fallback to moving average
            window = 7
            test_predictions = np.array([train_data[-window:].mean()] * test_size)
            future_forecast = np.array([data[-window:].mean()] * forecast_days)
    
    elif best_type == 'ETS':
        try:
            model = ExponentialSmoothing(train_data, trend='add', seasonal=None, damped_trend=True)
            fit = model.fit()
            test_predictions = fit.forecast(steps=test_size)
            
            # Retrain on full data
            full_model = ExponentialSmoothing(data, trend='add', seasonal=None, damped_trend=True)
            full_fit = full_model.fit()
            future_forecast = full_fit.forecast(steps=forecast_days)
        except:
            window = 7
            test_predictions = np.array([train_data[-window:].mean()] * test_size)
            future_forecast = np.array([data[-window:].mean()] * forecast_days)
    
    else:  # Moving Average baseline
        window = best_config
        test_predictions = np.array([train_data[-window:].mean()] * test_size)
        future_forecast = np.array([data[-window:].mean()] * forecast_days)
    
    # Calculate metrics
    mae = mean_absolute_error(test_data, test_predictions)
    r2 = r2_score(test_data, test_predictions)
    
    # Avoid division by zero in MAPE
    mape = mean_absolute_percentage_error(test_data, test_predictions) * 100 if test_data.min() > 0 else 0
    
    # Generate future dates
    last_date = df.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days, freq='D')
    
    predictions_df = pd.DataFrame({
        'Date': future_dates, 
        'Amount': future_forecast
    })
    
    metrics = {
        'mae': round(mae, 2),
        'r2': round(r2, 4),
        'mape': round(mape, 2),
        'best_model': f"{best_type} {best_config}" if best_type else "Unknown"
    }
    
    return predictions_df, metrics

@require_GET
def api_predict(request):
    """
    Optimized JSON endpoint with aggressive caching.
    """
    # Parse and validate params
    try:
        days = int(request.GET.get('forecast_days', 14))
    except (ValueError, TypeError):
        days = 14
    days = max(1, min(days, 30))

    model_hint = request.GET.get('model', '').lower()
    ci_flag = request.GET.get('ci', '0') == '1'
    
    # Create cache key based on parameters
    cache_key = f'prediction_api_{days}_{model_hint}_{ci_flag}'
    cached_response = cache.get(cache_key)
    
    if cached_response is not None:
        return JsonResponse(cached_response)

    # Build the historical dataframe using existing helper
    try:
        df = prepare_data()
    except Exception as exc:
        return JsonResponse({'error': 'failed to prepare data', 'detail': str(exc)}, status=500)

    if df is None or df.empty:
        return JsonResponse({'prediction': [], 'metrics': {}}, status=200)

    # Call core prediction routine
    try:
        predictions_df, metrics = train_and_predict(df, forecast_days=days)
    except Exception as exc:
        return JsonResponse({'error': 'prediction failed', 'detail': str(exc)}, status=500)

    # Format predictions as [timestamp_ms, value] to match Highcharts
    try:
        preds_list = []
        for _, row in predictions_df.iterrows():
            ts = int(pd.Timestamp(row['Date']).timestamp() * 1000)
            val = float(row['Amount'])
            preds_list.append([ts, val])
    except Exception as exc:
        return JsonResponse({'error': 'failed to format predictions', 'detail': str(exc)}, status=500)

    response_data = {
        'prediction': preds_list,
        'metrics': metrics,
        'forecast_days': days,
        'model_hint': model_hint,
        'ci': ci_flag
    }
    
    # Cache for 30 minutes (1800 seconds)
    cache.set(cache_key, response_data, 1800)
    
    return JsonResponse(response_data, status=200)