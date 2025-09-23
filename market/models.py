from django.db import models
from django.conf import settings

class SugarListing(models.Model):
    """
    This model represents sugar products in the marketplace
    """
    seller = models.ForeignKey('users.Seller', on_delete=models.CASCADE, null=True, blank=True, db_constraint=False)
    sugar_type = models.CharField(max_length=255)
    origin = models.CharField(max_length=255)
    quantity_available = models.PositiveIntegerField(help_text="In 50kg bags")
    price_per_bag = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per 50kg bag")
    minimum_order_quantity = models.PositiveIntegerField(help_text="In 50kg bags")
    specifications = models.TextField()

    def __str__(self):
        """
        String concatenation of models for easy identification
        """
        return f'{self.sugar_type} from {self.origin}'

class Order(models.Model):
    """
    This model represents a transaction record for a sugar product purchase
    """
    # Define status choices
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Delivered', 'Delivered'),
    ]

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_constraint=False) #Buyer is a user
    # Add related_name for easier reverse lookup
    listing = models.ForeignKey(SugarListing, related_name='orders', on_delete=models.CASCADE) #product is ordered
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String concatenation of models for easy identification
        """
        return f'Order #{self.id} by {self.buyer.username}'