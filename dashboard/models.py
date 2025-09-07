from django.db import models

class SugarPrice(models.Model):
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.date} - {self.amount}'