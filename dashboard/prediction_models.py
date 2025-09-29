import pandas as pd
from .models import SugarPrice
from sklearn.linear_model import LinearRegression
import numpy as np
# Import necessary metrics from scikit-learn
from sklearn.metrics import mean_absolute_error, r2_score

def prepare_data():
    """
    Prepares data for model training.
    """
    prices = SugarPrice.objects.all().values('date', 'amount')
    df = pd.DataFrame(list(prices))
    df = df.rename(columns={'date': 'Date','amount': 'Amount'})
    df = df.sort_values(by='Date')
    return df

def train_and_predict(df):
    """
    Features a simple linear regression model to predict future sugar prices
    and evaluates its accuracy on a held-out test set.
    """
    # --- Model Evaluation ---
    # Split data into training and testing sets (e.g., last 30 days for testing)
    train_df = df.iloc[:-30]
    test_df = df.iloc[-30:]

    # Prepare data for scikit-learn
    train_df = train_df.copy()
    train_df['Time'] = (pd.to_datetime(train_df['Date']) - pd.to_datetime(train_df['Date']).min()).dt.days
    X_train = train_df[['Time']]
    y_train = train_df['Amount']

    test_df = test_df.copy()
    test_df['Time'] = (pd.to_datetime(test_df['Date']) - pd.to_datetime(df['Date']).min()).dt.days
    X_test = test_df[['Time']]
    y_test = test_df['Amount']
    
    # Train the model on the training data
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Make predictions on the test set
    test_predictions = model.predict(X_test)

    # Calculate accuracy metrics
    mae = mean_absolute_error(y_test, test_predictions)
    r2 = r2_score(y_test, test_predictions)
    
    # --- Future Predictions (using the full dataset) ---
    df_full = df.copy()
    df_full['Date'] = pd.to_datetime(df_full['Date'])
    df_full['Time'] = (df_full['Date'] - df_full['Date'].min()).dt.days
    X_full = df_full[['Time']]
    y_full = df_full['Amount']
    
    # Retrain the model on the entire dataset for future predictions
    model.fit(X_full, y_full)
    
    last_time = X_full.iloc[-1]['Time']
    future_times_array = np.array(range(last_time + 1, last_time + 31)).reshape(-1, 1)
    future_times_df = pd.DataFrame(future_times_array, columns=['Time'])
    future_predictions = model.predict(future_times_df)
    
    last_date = df_full['Date'].iloc[-1]
    future_dates = pd.to_datetime([last_date + pd.Timedelta(days=i) for i in range(1, 31)])
    predictions_df = pd.DataFrame({'Date': future_dates, 'Amount': future_predictions})
    
    # Return both the future predictions and the accuracy metrics
    return predictions_df, {'mae': mae, 'r2': r2}