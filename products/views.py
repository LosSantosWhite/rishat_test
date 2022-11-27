from django.shortcuts import get_object_or_404
from django.views.generic import DeleteView, ListView
from django.views import View
from django.http.response import JsonResponse
from django.conf import settings
import stripe

from products.models import Item


class ItemList(ListView):
    template_name = "item_list.html"
    context_object_name = "items"
    model = Item


class ItemView(DeleteView):
    model = Item
    template_name = "item_detail.html"
    context_object_name = "item"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe_publish_key"] = settings.STRIPE_PUBLISH_KEY
        return context


class StripeConfig(View):
    domain_url = "http://localhost:8000/"

    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Item, pk=self.kwargs["pk"])
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=self.domain_url
                + "success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=self.domain_url + "cancelled/",
                payment_method_types=["card"],
                mode="payment",
                currency="usd",
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product": str(item.id),
                            "unit_amount": item.price,
                        },
                        "quantity": 1,
                    }
                ],
            )
            print(checkout_session)
        except Exception as e:
            return JsonResponse({"error": str(e)})
        return JsonResponse({"sessionId": checkout_session["id"]})
