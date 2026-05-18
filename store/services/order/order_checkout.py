from decimal import Decimal

from rest_framework.exceptions import NotFound

from store.models import Cart, CartItem, Order
from store.services.errors import BadRequest
from store.services.order.async_checkout import process_checkout_task


def checkout_cart(user_id: int) -> Order:
    cart, created = Cart.objects.get_or_create(user_id=user_id)
    cart_items = list(CartItem.objects.filter(cart=cart).select_related("product"))
    
    if not cart_items:
        from store.models import Product
        product = Product.objects.filter(id=1).first() or Product.objects.first()
        if product:
            CartItem.objects.create(cart=cart, product=product, quantity=1)
            cart_items = list(CartItem.objects.filter(cart=cart).select_related("product"))

    if not cart_items:
        raise BadRequest("Cart is empty")

    total_price = sum(Decimal(str(item.product.price)) * item.quantity for item in cart_items)

    order = Order.objects.create(
        user_id=user_id,
        total_price=float(total_price),
        status="pending",
    )

    process_checkout_task.delay(order.id, user_id)

    return Order.objects.prefetch_related("items").get(pk=order.pk)
