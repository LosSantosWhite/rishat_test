from django.db import models
from django.urls import reverse
import stripe


class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=0, max_digits=8)
    description = models.TextField()

    def __str__(self) -> str:
        return f"{self.name} -- {self.price}"

    def save(self, *args, **kwargs) -> None:
        """
        Change save method for
        1. Create product in stripe if dont exists
        2. Update product in stripe if it changed
        """
        if not self.id:
            super().save(*args, **kwargs)

            stripe.Product.create(
                id=str(self.id),
                name=str(self.name),
                description=str(self.description),
                default_price_data={
                    "currency": "usd",
                    "unit_amount_decimal": str(self.price),
                },
            )

        else:
            super().save(*args, **kwargs)  # ???
            price = stripe.Price.create(
                product=str(self.id),
                unit_amount=self.price,
                currency="usd",
            )
            stripe.Product.modify(
                str(self.id),
                name=self.name,
                description=self.description,
                default_price=price.id,
            )

    def delete(self, *args, **kwargs):
        """
        Move product in stripe's archive when it was deleted in model
        """
        stripe.Product.modify(str(self.id), active=False)
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("item_detail", kwargs={"pk": self.pk})
