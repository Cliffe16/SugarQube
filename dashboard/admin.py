from django.contrib import admin
from .models import SugarPrice

@admin.register(SugarPrice)
class SugarPriceAdmin(admin.ModelAdmin):
    list_display = ['date', 'amount', 'rate']
    list_filter = ['date']
    ordering = ['-date']