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

def train_and_predict(df, forecast_days=14, model_hint='auto'):
    """
    Main function that orchestrates prediction.
    Now supports:
      - model_hint: 'auto' (default), 'arima', 'ets', 'ma' (moving average)
    Returns:
      predictions_df, metrics_summary, per_model_metrics_dict
    """
    if df.empty or len(df) < 40:
        empty_metrics = {'mae': 0, 'r2': 0, 'mape': 0, 'best_model': 'Unknown'}
        return pd.DataFrame(), empty_metrics, {}

    forecast_days = max(1, min(forecast_days, 30))
    data = df['Amount'].copy()

    # Use validation split for internal comparisons
    test_size = min(30, len(data) // 4)
    # Get the auto-selected best model config (for ARIMA config fallback)
    auto_best_type, auto_best_config, _ = find_best_model(data, test_size)

    # Helper functions to compute predictions + metrics for each model
    def _compute_arima(data_series):
        try:
            order = auto_best_config if (isinstance(auto_best_config, tuple) and auto_best_type == 'ARIMA') else (1, 1, 1)
            # Walk-forward on full series for test portion
            test_preds, _ = walk_forward_validation(data_series, order, test_size)
            full_model = ARIMA(data_series, order=order)
            full_fit = full_model.fit()
            future_forecast = full_fit.forecast(steps=forecast_days)
        except Exception:
            window = 7
            train_data = data_series[:-test_size]
            test_preds = np.array([train_data[-window:].mean()] * test_size)
            future_forecast = np.array([data_series[-window:].mean()] * forecast_days)
        return test_preds, np.array(future_forecast)

    def _compute_ets(data_series):
        try:
            train_data = data_series[:-test_size]
            model = ExponentialSmoothing(train_data, trend='add', seasonal=None, damped_trend=True)
            fit = model.fit()
            test_preds = fit.forecast(steps=test_size)

            full_model = ExponentialSmoothing(data_series, trend='add', seasonal=None, damped_trend=True)
            full_fit = full_model.fit()
            future_forecast = full_fit.forecast(steps=forecast_days)
        except Exception:
            window = 7
            train_data = data_series[:-test_size]
            test_preds = np.array([train_data[-window:].mean()] * test_size)
            future_forecast = np.array([data_series[-window:].mean()] * forecast_days)
        return np.array(test_preds), np.array(future_forecast)

    def _compute_ma(data_series, window=7):
        train_data = data_series[:-test_size]
        test_preds = np.array([train_data[-window:].mean()] * test_size)
        future_forecast = np.array([data_series[-window:].mean()] * forecast_days)
        return test_preds, future_forecast

    # Compute per-model preds + metrics
    per_model_metrics = {}

    # ARIMA
    arima_test_preds, arima_future = _compute_arima(data)
    arima_test_actual = data[-test_size:]
    try:
        arima_mae = mean_absolute_error(arima_test_actual, arima_test_preds)
        arima_r2 = r2_score(arima_test_actual, arima_test_preds)
        arima_mape = mean_absolute_percentage_error(arima_test_actual, arima_test_preds) * 100 if arima_test_actual.min() > 0 else 0
    except Exception:
        arima_mae, arima_r2, arima_mape = float('inf'), 0, 0

    per_model_metrics['ARIMA'] = {
        'mae': round(float(arima_mae), 2) if np.isfinite(arima_mae) else None,
        'r2': round(float(arima_r2), 4) if np.isfinite(arima_r2) else None,
        'mape': round(float(arima_mape), 2) if np.isfinite(arima_mape) else None,
        'forecast': list(map(float, np.array(arima_future).ravel()))
    }

    # ETS
    ets_test_preds, ets_future = _compute_ets(data)
    ets_test_actual = data[-test_size:]
    try:
        ets_mae = mean_absolute_error(ets_test_actual, ets_test_preds)
        ets_r2 = r2_score(ets_test_actual, ets_test_preds)
        ets_mape = mean_absolute_percentage_error(ets_test_actual, ets_test_preds) * 100 if ets_test_actual.min() > 0 else 0
    except Exception:
        ets_mae, ets_r2, ets_mape = float('inf'), 0, 0

    per_model_metrics['ETS'] = {
        'mae': round(float(ets_mae), 2) if np.isfinite(ets_mae) else None,
        'r2': round(float(ets_r2), 4) if np.isfinite(ets_r2) else None,
        'mape': round(float(ets_mape), 2) if np.isfinite(ets_mape) else None,
        'forecast': list(map(float, np.array(ets_future).ravel()))
    }

    # Moving Average baseline
    window = min(7, max(1, len(data) // 20))
    ma_test_preds, ma_future = _compute_ma(data, window=window)
    ma_test_actual = data[-test_size:]
    try:
        ma_mae = mean_absolute_error(ma_test_actual, ma_test_preds)
        ma_r2 = r2_score(ma_test_actual, ma_test_preds)
        ma_mape = mean_absolute_percentage_error(ma_test_actual, ma_test_preds) * 100 if ma_test_actual.min() > 0 else 0
    except Exception:
        ma_mae, ma_r2, ma_mape = float('inf'), 0, 0

    per_model_metrics['MA'] = {
        'mae': round(float(ma_mae), 2) if np.isfinite(ma_mae) else None,
        'r2': round(float(ma_r2), 4) if np.isfinite(ma_r2) else None,
        'mape': round(float(ma_mape), 2) if np.isfinite(ma_mape) else None,
        'forecast': list(map(float, np.array(ma_future).ravel())),
        'window': int(window)
    }

    # Decide which model to return for the "prediction" array based on model_hint
    selected_model_key = (model_hint or 'auto').lower()
    if selected_model_key in ('arima', 'ets', 'ma'):
        chosen_key = selected_model_key.upper()
    else:
        # fallback to the best by MAE
        best = min(per_model_metrics.items(), key=lambda kv: (kv[1]['mae'] if kv[1]['mae'] is not None else float('inf')))
        chosen_key = best[0]

    # Build predictions_df using the chosen model's forecast
    chosen_forecast = per_model_metrics[chosen_key]['forecast']
    last_date = df.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days, freq='D')

    predictions_df = pd.DataFrame({
        'Date': future_dates,
        'Amount': chosen_forecast
    })

    # Build summary metrics (the "best" model string and values)
    summary = {
        'mae': per_model_metrics[chosen_key]['mae'],
        'r2': per_model_metrics[chosen_key]['r2'],
        'mape': per_model_metrics[chosen_key]['mape'],
        'best_model': f"{chosen_key}"
    }

    return predictions_df, summary, per_model_metrics


@require_GET
def api_predict(request):
    """
    Optimized JSON endpoint with aggressive caching.
    Now:
      - Accepts model hint and returns per-model metrics as 'all_metrics'.
    """
    try:
        days = int(request.GET.get('forecast_days', 14))
    except (ValueError, TypeError):
        days = 14
    days = max(1, min(days, 30))

    model_hint = (request.GET.get('model', '') or 'auto').lower()
    ci_flag = request.GET.get('ci', '0') == '1'

    cache_key = f'prediction_api_{days}_{model_hint}_{ci_flag}'
    cached_response = cache.get(cache_key)
    if cached_response is not None:
        return JsonResponse(cached_response)

    try:
        df = prepare_data()
    except Exception as exc:
        return JsonResponse({'error': 'failed to prepare data', 'detail': str(exc)}, status=500)

    if df is None or df.empty:
        return JsonResponse({'prediction': [], 'metrics': {}, 'all_metrics': {}}, status=200)

    try:
        predictions_df, metrics_summary, all_metrics = train_and_predict(df, forecast_days=days, model_hint=model_hint)
    except Exception as exc:
        return JsonResponse({'error': 'prediction failed', 'detail': str(exc)}, status=500)

    # Format predictions for Highcharts: [timestamp_ms, value]
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
        'metrics': metrics_summary,
        'all_metrics': all_metrics,
        'forecast_days': days,
        'model_hint': model_hint,
        'ci': ci_flag
    }

    cache.set(cache_key, response_data, 1800)
    return JsonResponse(response_data, status=200)

