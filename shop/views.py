from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.conf import settings
from django.http import JsonResponse
from decimal import Decimal
import razorpay
from .models import Product, Cart, CartItem, Order, OrderItem ,Contact
from .forms import CartItemForm,contactform
from django.db.models import Sum, Count


def get_or_create_cart(request):
    """
    Get or create cart based on user or session.
    For authenticated users: use user field
    For guests: use session_id from Django session
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # Ensure session exists
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_id=request.session.session_key)
    return cart




def cart_count(request):
    cart = get_or_create_cart(request)

    count = cart.cartitem_set.count()


    return {
        'cart_count': count
    }




def product_list(request):
    products = Product.objects.all()

    return render(request, 'shop/product_list.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})


# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, pk=product_id)
#     cart = get_or_create_cart(request)

#     # Check stock
#     if not product.is_available():
#         messages.error(request, "Product is out of stock.")
#         return redirect('product_detail', pk=product_id)

#     cart_item, created = CartItem.objects.get_or_create(
#         cart=cart,
#         product=product,
#         defaults={'quantity': 1}
#     )
#     if not created:
#         if not product.is_available(cart_item.quantity + 1):
#             messages.error(request, "Not enough stock available.")
#             return redirect('product_detail', pk=product_id)
#         cart_item.quantity += 1
#         cart_item.save()

#     messages.success(request, f"{product.name} added to cart.")
#     return redirect('product_list')







# views.py

from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    product = Product.objects.get(id=product_id)

   
    cart = get_or_create_cart(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    cart_count = cart.cartitem_set.count()

    return JsonResponse({
        'status': 'success',
        'cart_count': cart_count
    })





# def updatequantity(request):
#     pid = request.POST.get('pro_id')
#     quantity = request.POST.get('quantity')
#     print(pid,quantity,"____________________________")

#     try:
#         quantity = int(quantity)
#         if quantity < 1:
#             quantity = 1
#     except ValueError:
#         quantity = 1

#     cart = get_or_create_cart(request)
#     product = get_object_or_404(Product, pk=pid)

#     cart_item, created = CartItem.objects.get_or_create(
#         cart=cart,
#         product=product,
#         defaults={'quantity': quantity}
#     )
#     if not created:
#         # Check if increasing quantity exceeds stock
#         if not product.is_available(cart_item.quantity + int(quantity)):
#             messages.error(request, "Not enough stock available.")
#             return redirect('product_detail', pk=pid)
#         cart_item.quantity += int(quantity)
#         cart_item.save()

#     messages.success(request, f"{product.name} addedto card new.")
#     return redirect(cart_view)










def buy_now(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == "POST":
        quantity = int(request.POST.get('quantity', 1))

        # Validate stock
        if not product.is_available(quantity):
            messages.error(request, "Not enough stock available.")
            return redirect('product_detail', pk=product_id)

        if quantity < 1:
            quantity = 1

        # Store in session
        request.session['buy_now_product'] = product_id
        request.session['buy_now_quantity'] = quantity

        messages.success(request, f"Proceeding to checkout for {product.name}.")
        return redirect('checkout')

    return redirect('checkout')


def cart_view(request):
    cart = get_or_create_cart(request)
  
    cart_items = cart.cartitem_set.select_related('product').all()

    request.session.pop('buy_now_product', None)
    request.session.pop('buy_now_quantity', None)
    # cart_items = cart.cartitem_set.select_related('product').all()

    total = cart.total_amount

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        if action == 'update':
            form = CartItemForm(request.POST, instance=cart_item)
            if form.is_valid():
                quantity = form.cleaned_data['quantity']
                if not cart_item.product.is_available(quantity):
                    messages.error(request, "Not enough stock available.")
                else:
                    form.save()
                    messages.success(request, "Quantity updated.")
        elif action == 'remove':
            cart_item.delete()
            messages.success(request, "Item removed from cart.")

        return redirect('cart')

    # Forms for each item
    item_forms = {item.id: CartItemForm(instance=item) for item in cart_items}

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'item_forms': item_forms,
    })


def checkout(request):
    # Check if this is a buy_now checkout
    buy_now_product_id = request.session.get('buy_now_product')
    buy_now_quantity = request.session.get('buy_now_quantity', 1)

    if buy_now_product_id:
        # Buy Now flow: single product checkout
        product = get_object_or_404(Product, pk=buy_now_product_id)
        if not product.is_available(buy_now_quantity):
            messages.error(request, f"Not enough stock for {product.name}.")
            # Clear buy_now session
            del request.session['buy_now_product']
            del request.session['buy_now_quantity']
            return redirect('product_detail', pk=buy_now_product_id)

        cart_items = [{'product': product, 'quantity': buy_now_quantity, 'subtotal': product.price * buy_now_quantity}]
        total = product.price * buy_now_quantity
        is_buy_now = True
    else:
        # Regular cart checkout
        cart = get_or_create_cart(request)
        cart_items = cart.cartitem_set.all()

        if not cart_items:
            messages.error(request, "Your cart is empty.")
            return redirect('product_list')

        # Recalculate total server-side (never trust frontend)
        total = sum(item.subtotal for item in cart_items)

        # Validate stock again
        for item in cart_items:
            if not item.product.is_available(item.quantity):
                messages.error(request, f"Not enough stock for {item.product.name}.")
                return redirect('cart')

        is_buy_now = False

    if request.method == 'POST':
        # Create Razorpay order
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            "amount": int(total * 100),  # Amount in paisa
            "currency": "INR",
            "payment_capture": 1
        })

        # Create Order object
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            total_amount=total,
            razorpay_order_id=razorpay_order['id'],
            payment_status='PENDING'
        )

        # Store order_id in session for buy_now
        if is_buy_now:
            request.session['buy_now_order'] = order.id

        return render(request, 'shop/checkout.html', {
            'cart_items': cart_items,
            'total': total,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'order': order,
            'is_buy_now': is_buy_now,
        })

    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'is_buy_now': is_buy_now,
    })


def payment_success(request):
    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    razorpay_order_id = request.GET.get('razorpay_order_id')
    razorpay_signature = request.GET.get('razorpay_signature')

    if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        messages.error(request, "Invalid payment data.")
        return redirect('checkout')

    try:
        order = Order.objects.get(razorpay_order_id=razorpay_order_id)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('checkout')

    # Verify signature
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
    except razorpay.errors.SignatureVerificationError:
        order.payment_status = 'FAILED'
        order.save()
        messages.error(request, "Payment verification failed.")
        return redirect('payment_failed')

    # Payment verified, process order
    buy_now_order_id = request.session.get('buy_now_order')
    if buy_now_order_id and str(order.id) == str(buy_now_order_id):
        # Buy Now order: create OrderItem from session data
        product_id = request.session.get('buy_now_product')
        quantity = request.session.get('buy_now_quantity', 1)
        product = get_object_or_404(Product, pk=product_id)

        with transaction.atomic():
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
            # Reduce stock
            product.stock -= quantity
            product.save()

            # Update order
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.payment_status = 'SUCCESS'
            order.save()

            # Clear buy_now session
            if 'buy_now_product' in request.session:
                del request.session['buy_now_product']
            if 'buy_now_quantity' in request.session:
                del request.session['buy_now_quantity']
            if 'buy_now_order' in request.session:
                del request.session['buy_now_order']
    else:
        # Regular cart order
        cart = get_or_create_cart(request)
        cart_items = cart.cartitem_set.all()

        with transaction.atomic():
            # Create OrderItems
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                # Reduce stock
                item.product.stock -= item.quantity
                item.product.save()

            # Update order
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.payment_status = 'SUCCESS'
            order.save()

            # Clear cart
            cart_items.delete()

    messages.success(request, "Payment successful! Your order has been placed.")
    return redirect('payment_success_page')


def payment_failed(request):
    messages.error(request, "Payment failed. Please try again.")
    return redirect('checkout')


def payment_success_page(request):
    return render(request, 'shop/payment_success.html')





@require_POST
def update_cart_quantity(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity'))

    try:
        cart = get_or_create_cart(request)

        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        cart_item.quantity = quantity
        cart_item.save()


        product = cart_item.product
        subtotal = product.price * quantity

        # subproduct = Product.objects.get(id=product_id)
        # subtotal = subproduct.price * quantity
        # print("______________",subtotal)
    except Exception:
        return messages.error("No cart appeared")

    # cart_count = cart.cartitem_set.aggregate(Sum('quantity'))['quantity__sum'] or 0

    return JsonResponse({
        'status': 'success',
        'subtotal':float(subtotal)
        # 'cart_count': cart_count
    })



























def contact(request):




    if request.method == "POST":
        form = contactform(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success':True
            })
        return JsonResponse({
            'success' :False
        })
    else:
        print("contyact caleed______________________")



        form = contactform()
        print(settings.RAZORPAY_API_KEY,"___________________________")



    return render(request , 'shop/contact.html',{'form':form})




