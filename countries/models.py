from django.db import models

# Country model creation
class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)
    capital = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    population = models.BigIntegerField()
    currency_code = models.CharField(max_length=10, null=True, blank=True)
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    estimated_gdp = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    flag_url = models.URLField(max_length=500, null=True, blank=True)
    last_refreshed_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'countries'
        ordering = ['name']

    def __str__(self):
        return self.name