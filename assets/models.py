from decimal import Decimal
from django.db import models
from django.db.models import F, Sum, DecimalField, OuterRef, Subquery

class Asset(models.Model):
    """A global catalog of tradeable assets."""
    name   = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Portfolio(models.Model):
    name       = models.CharField(max_length=255)
    created_at = models.DateField()

    def __str__(self):
        return self.name

    def total_value(self, on_date):
        # Build a subquery: price for each holding’s asset
        price_qs = AssetPrice.objects.filter(
            asset=OuterRef('asset__pk'),
            date=on_date
        ).values('price')[:1]

        agg = self.holdings.annotate(
            price_on_date=Subquery(price_qs, output_field=DecimalField())
        ).aggregate(
            total=Sum(
                F('amount') * F('price_on_date'),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            )
        )
        return agg['total'] or Decimal('0.00')

    def asset_weights(self, on_date):
        total = self.total_value(on_date)
        if total == 0:
            return {h.asset.name: Decimal('0.0000') for h in self.holdings.all()}

        return {
            h.asset.name: (h.amount * h.price_on(on_date) / total).quantize(Decimal("0.0001"))
            for h in self.holdings.all()
        }


class PortfolioAsset(models.Model):
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='holdings'
    )
    asset      = models.ForeignKey(Asset, on_delete=models.PROTECT)
    weight     = models.DecimalField(max_digits=4, decimal_places=2)
    amount     = models.DecimalField(max_digits=20, decimal_places=4,default=0)

    class Meta:
        unique_together = ('portfolio','asset')

    def __str__(self):
        return f"{self.portfolio}→{self.asset}"

    def price_on(self, on_date):
        """Helper: fetch this asset’s price on a given date."""
        try:
            return self.asset.prices.get(date=on_date).price
        except AssetPrice.DoesNotExist:
            return Decimal('0')

    def market_value(self, on_date):
        return (self.amount * self.price_on(on_date)).quantize(Decimal('0.01'))


class AssetPrice(models.Model):
    """
    Daily price for each global Asset.
    """
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='prices')
    date  = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('asset','date')

    def __str__(self):
        return f"{self.asset.name} @ {self.date}: {self.price}"
