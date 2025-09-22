import pandas as pd
from .models import SugarPrice
from sklearn.linear_model import LinearRegression
import numpy as np

def prepare_data():
    """
    Prepares data for model training.
    """
    # Fetch all sugar price records from the database
    prices = SugarPrice.objects.all().values('date', 'amount')
    
    # Convert the queryset to a pandas DataFrame
    df = pd.DataFrame(list(prices))
    
    # Rename columns
    df = df.rename(columns={'date': 'Date','amount': 'Amount'})
    
    #Sort the data by date
    df = df.sort_values(by='Date')
    
    return df

def train_and_predict(df):
    """
    Features a simple linear regression model to predict future sugar prices.
    """
    # Prepare the data
    # convert the date to numbers(no. of years from the start date)
    df_model = df.copy()
    df_model['Time'] = (df_model['Date'] - df_model['Date'].min()).dt.days
    
    # Prepare data for scikit-learn
    # X needs to be 2D array
    X = df_model[['Time']]
    # y is the target variable
    y = df_model['Amount']
    
    # Train the model
    model = LinearRegression()
    model.fit(X, y)
    
    # Make predictions for the next 30 days
    last_time = X.iloc[-1]['Time']
    future_times = np.array(range(last_time + 1, last_time + 31)).reshape(-1, 1)
    
    # Get the predictions for these future times
    future_predictions = model.predict(future_times)
    
    # Get the actual future dates
    last_date = df_model['Date'].iloc[-1]
    future_dates = pd.to_datetime([last_date + pd.Timedelta(days=i) for i in range(1, 31)])
    
    # Combine future dates and predictions into a DataFrame
    predictions_df = pd.DataFrame({'Date': future_dates, 'Amount': future_predictions})
    
    return predictions_df
    
    