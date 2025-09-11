from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import SugarListing, Order
from .forms import OrderForm

def listing_list(request):
    listings = SugarListing.objects.filter(quantity_available__gt=0).order_by('sugar_type')
    return render(request, 'trading/listing_list.html', {'listings': listings})

@login_required
def listing_detail(request, pk):
    listing = get_object_or_404(SugarListing, pk=pk)
    form = OrderForm()
    return render(request, 'trading/listing_detail.html', {'listing': listing, 'form': form})

@login_required
@transaction.atomic
def place_order(request, pk):
    if not request.user.is_verified_buyer:
        messages.error(request, 'You must be a verified buyer to place an order.')
        return redirect('listing_list')

    listing = get_object_or_404(SugarListing, pk=pk)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']

            if quantity < listing.minimum_order_quantity:
                messages.error(request, f'The minimum order quantity is {listing.minimum_order_quantity} bags.')
            elif quantity > listing.quantity_available:
                messages.error(request, 'The requested quantity exceeds available stock.')
            else:
                total_price = quantity * listing.price_per_bag
                Order.objects.create(
                    buyer=request.user,
                    listing=listing,
                    quantity=quantity,
                    total_price=total_price,
                    status='Pending'
                )
                listing.quantity_available -= quantity
                listing.save()

                messages.success(request, 'Your order has been placed successfully!')
                return redirect('order_history')
    else:
        # This case should not be hit directly, redirecting for safety
        return redirect('listing_detail', pk=pk)

    # If form is invalid or has errors, re-render the detail page
    return render(request, 'trading/listing_detail.html', {'listing': listing, 'form': form})

@login_required
def order_history(request):
    # Get sorting parameters from the URL (e.g., ?sort=status&dir=asc)
    sort_by = request.GET.get('sort', 'created_at')
    sort_dir = request.GET.get('dir', 'desc')

    # Whitelist of fields users are allowed to sort by for security
    valid_sort_fields = ['id', 'created_at', 'listing__sugar_type', 'quantity', 'total_price', 'status']
    if sort_by not in valid_sort_fields:
        sort_by = 'created_at' # Default to sorting by date if invalid field is provided

    # Determine the sorting direction and build the ordering string
    if sort_dir == 'desc':
        ordering = f'-{sort_by}'
        next_sort_dir = 'asc'
    else:
        ordering = sort_by
        next_sort_dir = 'desc'

    # Query the database with the dynamic ordering
    orders = Order.objects.filter(buyer=request.user).order_by(ordering)

    context = {
        'orders': orders,
        'sort_by': sort_by,
        'sort_dir': sort_dir,
        'next_sort_dir': next_sort_dir
    }
    return render(request, 'trading/order_history.html', context)