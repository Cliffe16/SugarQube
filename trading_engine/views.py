from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def trading_home(request):
    """
    Placeholder view for the trading engine interface.
    """
    return render(request, 'trading_engine/trading_home.html')