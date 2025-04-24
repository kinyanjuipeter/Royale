from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import RedirectView
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem, Category, Order, OrderItem, Customer, Promotion
from django.views.decorators.http import require_POST
from registration.models import Customer  # Import Customer from registration app
from .forms import CartAddProductForm
from django.db.models import Q
from django.utils import timezone
from django.db import models

# Redirect views for legacy URLs
def product_list_redirect(request):
    return redirect('/', permanent=True)

def product_detail_redirect(request, id, slug):
    return redirect(f'/{id}/{slug}/', permanent=True) 

def cart_detail_redirect(request):
    return redirect('/cart/', permanent=True)

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Get active promotion
    active_promotion = Promotion.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).first()
    
    # Handle sorting
    sort_by = request.GET.get('sort', '')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'top_rated':
        products = products.annotate(avg_rating=models.Avg('reviews__rating')).order_by('-avg_rating')
    
    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'active_promotion': active_promotion,
        'current_sort': sort_by,
    }
    return render(request, 'shop/product/list.html', context)

def product_detail(request, id, slug):
    product = get_object_or_404(Product,
                               id=id,
                               slug=slug,
                               available=True)
    return render(request,
                 'shop/product/detail.html',
                 {'product': product})

def cart_detail(request):
    cart_items_data = []  # Use a different name to avoid confusion
    total = 0
    
    if request.user.is_authenticated:
        cart = Cart.objects.filter(customer=request.user).first()
        if cart:
            # Iterate through CartItem instances and create dictionaries
            for item in cart.items.select_related('product').all():
                item_total = item.get_cost()
                cart_items_data.append({
                    'product': item.product,
                    'quantity': item.quantity,
                    'total_price': item_total
                })
                total += item_total
    else:
        session_cart = request.session.get('cart', [])
        for item_session in session_cart: # Renamed to avoid inner/outer scope clash
            product = get_object_or_404(Product, id=item_session['product_id'])
            quantity = item_session['quantity']
            item_total = product.price * quantity
            cart_items_data.append({
                'product': product,
                'quantity': quantity,
                'total_price': item_total
            })
            total += item_total
    
    context = {
        'cart_items': cart_items_data, # Pass the consistent list of dictionaries
        'total': total,
    }
    return render(request, 'shop/cart/detail.html', context)

def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > product.stock:
            messages.error(request, f"Only {product.stock} items available")
            return redirect('shop:product_detail', id=product.id, slug=product.slug)
        
        if request.user.is_authenticated:
            # Get or create cart for the user
            cart, created = Cart.objects.get_or_create(customer=request.user)
            # Get or create cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                if cart_item.quantity > product.stock:
                    messages.error(request, f"Only {product.stock} items available")
                    return redirect('shop:product_detail', id=product.id, slug=product.slug)
                cart_item.save()
            messages.success(request, "Added to cart")
        else:
            cart = request.session.get('cart', [])
                
            # Check if product already in cart
            for item in cart:
                if item['product_id'] == product.id:
                    item['quantity'] += quantity
                    if item['quantity'] > product.stock:
                        messages.error(request, f"Only {product.stock} items available")
                        return redirect('shop:product_detail', id=product.id, slug=product.slug)
                    request.session.modified = True
                    messages.success(request, "Cart updated")
                    break
            else:
                # Product not in cart, add it
                cart.append({
                    'product_id': product.id,
                    'quantity': quantity
                })
                request.session['cart'] = cart
                messages.success(request, "Added to cart")
                
    return redirect('shop:product_detail', id=product.id, slug=product.slug)

def order_confirmation(request):
    order_id = request.session.get('last_order')
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            # Clear the order from session after retrieving
            del request.session['last_order']
            
            return render(request, 'shop/orders/confirmation.html', {
                'order': order
            })
        except Order.DoesNotExist:
            messages.error(request, "Order not found")
    return redirect('shop:product_list')

def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(customer=request.user)
            cart_item = CartItem.objects.filter(cart=cart, product=product).first()
            if cart_item:
                cart_item.delete()
                messages.success(request, f"{product.name} removed from cart.")
            else:
                messages.warning(request, "Item not found in cart.")
        except Cart.DoesNotExist:
            messages.warning(request, "Cart not found.")
    else:
        cart = request.session.get('cart', [])
        cart = [item for item in cart if item['product_id'] != product_id]
        request.session['cart'] = cart
        messages.success(request, f"{product.name} removed from cart.")
    
    return redirect('shop:cart_detail')

def cart_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                raise ValueError("Quantity must be at least 1")
            
            if request.user.is_authenticated:
                cart = Cart.objects.filter(customer=request.user).first()
                if not cart:
                    cart = Cart.objects.create(customer=request.user)
                
                cart_item = CartItem.objects.filter(cart=cart, product=product).first()
                
                if cart_item:
                    cart_item.quantity = quantity
                    cart_item.save()
                    messages.success(request, f"{product.name} quantity updated.")
                else:
                    messages.warning(request, "Item not found in cart.")
            else:
                cart = request.session.get('cart', [])
                for item in cart:
                    if item['product_id'] == product_id:
                        item['quantity'] = quantity
                        break
                request.session['cart'] = cart
                messages.success(request, f"{product.name} quantity updated.")
                
        except (ValueError, TypeError):
            messages.error(request, "Invalid quantity provided.")
        except Exception as e:
            messages.error(request, "An error occurred while updating the cart.")
    
    return redirect('shop:cart_detail')

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

@require_POST
def guest_checkout(request):
    if request.method == 'POST':
        cart = request.session.get('cart', [])
        if not cart:
            messages.error(request, "Your cart is empty")
            return redirect('shop:cart_detail')
            
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        address = request.POST.get('address')
        
        # Validate required fields
        if not all([first_name, last_name, phone_number, address]):
            messages.error(request, "Please fill in all required fields")
            return redirect('shop:cart_detail')
            
        try:
            # Calculate total amount first
            total_amount = 0
            order_items = []
            
            for item in cart:
                try:
                    product = Product.objects.get(id=item['product_id'])
                    item_total = product.price * item['quantity']
                    total_amount += item_total
                    order_items.append({
                        'product': product,
                        'quantity': item['quantity'],
                        'price': product.price
                    })
                except Product.DoesNotExist:
                    continue
            
            # Create order for guest
            order = Order.objects.create(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                email=email,
                address=address,
                total_amount=total_amount,
                status='pending'
            )
            
            # Create order items
            for item in order_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
                
                # Update product stock
                product = item['product']
                product.stock -= item['quantity']
                product.save()
            
            # Clear cart and store order ID
            request.session['cart'] = []
            request.session['last_order'] = order.id
            
            messages.success(request, "Order placed successfully!")
            return redirect('shop:order_confirmation')
            
        except Exception as e:
            messages.error(request, "Error creating order. Please try again.")
            return redirect('shop:cart_detail')
            
    return redirect('shop:cart_detail')

import logging
logger = logging.getLogger(__name__)

@login_required
@require_POST
def create_order(request):
    """Handle order creation for authenticated users"""
    logger.info("Create order request received")
    try:
        customer = Customer.objects.get(username=request.user.username)
        cart = get_object_or_404(Cart, customer=customer)
        if not cart.items.exists():
            messages.error(request, "Your cart is empty")
            return redirect('shop:cart_detail')
            
        # Calculate total amount
        total_amount = sum(item.quantity * item.product.price for item in cart.items.all())
            
        # Create order with default values for required fields
        order = Order.objects.create(
            customer=customer,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            phone_number=customer.phone_number,
            address="To be provided",  # Default value since Customer model doesn't have address
            postal_code="00000",  # Default value
            city="Nairobi",  # Default value
            location=customer.location or "Nairobi",  # Use customer's location or default
            status='pending',
            total_amount=total_amount  # Set the calculated total amount
        )
        
        # Add all cart items to order
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )
        
        # Clear the cart
        cart.items.all().delete()
        
        # Store order ID in session
        request.session['last_order'] = order.id
        
        messages.success(request, "Order placed successfully!")
        return redirect('shop:order_confirmation')
        
    except Customer.DoesNotExist:
        messages.error(request, "You need to be a customer to place an order")
        return redirect('shop:cart_detail')
    except Exception as e:
        messages.error(request, f"Error placing order: {str(e)}")
        return redirect('shop:cart_detail')

@login_required
def my_orders(request):
    """Display orders for the logged-in customer"""
    orders = Order.objects.filter(customer=request.user).order_by('-created')
    return render(request, 'shop/orders/my_orders.html', {
        'orders': orders
    })

def search_products(request):
    """Handle product search functionality"""
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query) |
            Q(category__name__icontains=query)
        ).filter(available=True)
    
    context = {
        'products': products,
        'search_query': query,
        'categories': Category.objects.all()
    }
    return render(request, 'shop/product/search_results.html', context)
