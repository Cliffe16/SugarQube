from dashboard.models import SugarPrice

def currency_context(request):
    """
    Makes the latest exchange rate available to all templates.
    """
    latest_price_obj = SugarPrice.objects.order_by('date').last()

    if latest_price_obj:
        exchange_rate = float(latest_price_obj.rate)
    else:
        exchange_rate = 1.0  # Default value if no prices are in the DB

    return {
        'EXCHANGE_RATE_USD': exchange_rate
    }