import os
import sys
import time
from pathlib import Path
from decimal import Decimal

sys.path.append(str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce_backend.settings")

import django
django.setup()

from django.conf import settings
settings.CELERY_TASK_ALWAYS_EAGER = True

from store.models import User, Product, Cart, CartItem, Order
from store.services.order.order_checkout import checkout_cart

def test_async_payment():
    print("Starting Async Payment Test...")

    user, _ = User.objects.get_or_create(
        username="test_payer",
        defaults={"email": "test@example.com", "balance": 1000.0}
    )
    user.balance = 1000.0
    user.save()

    product, _ = Product.objects.get_or_create(
        name="Async Test Laptop",
        defaults={"price": 500.0, "stock_quantity": 10}
    )
    product.price = 500.0
    product.stock_quantity = 10
    product.save()

    cart, _ = Cart.objects.get_or_create(user=user)
    CartItem.objects.filter(cart=cart).delete()
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    print(f"Initial State: User Balance=${user.balance}, Product Stock={product.stock_quantity}")

    print("Triggering checkout...")
    order = checkout_cart(user.id)
    
    print(f"Response: Order ID={order.id}, Status={order.status}")
    if order.status not in ["pending", "completed"]:
        print(f"Error: Unexpected order status '{order.status}'.")
        return

    print("Waiting 3 seconds for Celery worker...")
    time.sleep(3)

    user.refresh_from_db()
    product.refresh_from_db()
    order.refresh_from_db()

    print(f"Final State: Order Status={order.status}, User Balance=${user.balance}, Product Stock={product.stock_quantity}")

    success = True
    if order.status != "completed":
        print("Error: Order status did not change to 'completed'. Check Celery logs.")
        success = False
    
    if user.balance != 500.0:
        print(f"Error: User balance should be 500.0, but got {user.balance}.")
        success = False

    if product.stock_quantity != 9:
        print(f"Error: Product stock should be 9, but got {product.stock_quantity}.")
        success = False

    if success:
        print("SUCCESS: Async payment and inventory update verified!")
    else:
        print("FAILED: One or more assertions failed.")

if __name__ == "__main__":
    test_async_payment()
