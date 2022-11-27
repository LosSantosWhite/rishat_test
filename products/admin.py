from django.contrib import admin
from products.models import Item


@admin.register(Item)
class AdminItem(admin.ModelAdmin):
    pass
