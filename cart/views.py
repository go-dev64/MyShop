from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from shop.models import Product

from .cart import Cart
from .forms import CartAddProductForm


def cart_detail(request):
    """
    Affiche le détail du panier.

    :param request: La requête HTTP reçue.
    :type request: HttpRequest
    :return: La réponse HTTP avec le détail du panier rendu
    dans le template "cart/detail.html".
    :rtype: HttpResponse
    """
    cart = Cart(request)
    for item in cart:
        item["update_quantity_form"] = CartAddProductForm(
            initial={"quantity": item["quantity"], "override": True}
        )
    return render(request, "cart/detail.html", {"cart": cart})


@require_POST
def cart_add(request, product_id):
    """
    Adds a product to the cart.

    :param request: The received HTTP request.
    :type request: HttpRequest
    :param product_id: The ID of the product to add.
    :type product_id: int
    :return: Redirects to the cart detail view.
    :rtype: HttpResponse
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product, quantity=cd["quantity"], override_quantity=cd["override"]
        )
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart:cart_detail")
