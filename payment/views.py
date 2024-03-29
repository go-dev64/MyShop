from decimal import Decimal

import stripe
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from config import settings
from orders.models import Order

# Create the Stipe instance
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_KEY


def payment_process(request):
    """View to handle payment process"""
    order_id = request.session.get("order_id", None)
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        success_url = request.build_absolute_uri(reverse("payment:completed"))
        cancel_url = request.build_absolute_uri(reverse("payment:canceled"))

        # Stripe checkout session data
        session_data = {
            "mode": "payment",
            "client_reference_id": order.id,  # type: ignore
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [],
        }
        # add order items to the Stripe checkout session
        for item in order.items.all():  # type: ignore
            session_data["line_items"].append(
                {
                    "price_data": {
                        "unit_amount": int(item.price * Decimal("100")),
                        "currency": "usd",
                        "product_data": {"name": item.product.name},
                    },
                    "quantity": item.quantity,
                }
            )
        # Stripe coupons
        if order.coupon:
            stripe_coupon = stripe.Coupon.create(
                name=order.coupon.code,
                percent_off=order.coupon.discount,
                duration="once",
            )
            session_data["discounts"] = [{"coupon": stripe_coupon.id}]
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(**session_data)
        # Redirect to Stripe payment form
        return redirect(session.url, code=303)
    else:
        return render(request, "payment/process.html", locals())


def payment_completed(request):
    """View to handle completed payments"""
    return render(request, "payment/completed.html")


def payment_canceled(request):
    """View to handle canceled payments"""
    return render(request, "payment/canceled.html")
