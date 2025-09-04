from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Product, Sale
# from .forms import SaleForm

from django.http import JsonResponse
from django.core import serializers


import json
import datetime

# Dummy product data for the example
products = [
    {'id': 1, 'name': 'Printing A4 color', 'price': 20.00},
    {'id': 2, 'name': 'Printing A4 B/W', 'price': 10.0},
    {'id': 3, 'name': 'Photocopy A4 color', 'price': 10.00},
    {'id': 4, 'name': 'Photocopy A4 B/W', 'price': 5.00},
    {'id': 5, 'name': 'Scanning', 'price': 20.00},
    {'id': 6, 'name': 'KRA nill returns', 'price': 100.00},
    {'id': 7, 'name': 'KRA P9', 'price': 150.00},
    {'id': 8, 'name': 'KRA reg', 'price': 200.00},
    {'id': 9, 'name': 'SHA/SHIF Registration', 'price': 200.00},
    {'id': 10, 'name': 'SHA/SHIF add dependant', 'price': 100.00},
    {'id': 11, 'name': 'Mail Services', 'price': 50.00},
    {'id': 12, 'name': 'Bowsing', 'price': 1},
    {'id': 13, 'name': 'Passport Photo', 'price': 25.00},
    {'id': 14, 'name': 'NTSA', 'price': 200.00},
    {'id': 15, 'name': 'HELB', 'price': 300.00},
    {'id': 16, 'name': 'Typesetting', 'price': 30.00},
    {'id': 17, 'name': 'TSE', 'price': 00.00},
    {'id': 18, 'name': 'Lamination A4', 'price': 50.00},
    {'id': 19, 'name': 'Lamination ID size', 'price': 30.00},
    {'id': 20, 'name': 'Printing Liscense', 'price': 30.00},
    {'id': 21, 'name': 'to add more end of thinking', 'price': 00.00},

    # {'id': 1, 'name': 'Laptop', 'price': 1200.00},
    # {'id': 2, 'name': 'Mouse', 'price': 25.50},
    # {'id': 3, 'name': 'Keyboard', 'price': 75.00},
    # {'id': 4, 'name': 'Monitor', 'price': 300.00},
]

# In a real application, this would be a database model.
# We'll use a list for demonstration purposes.
sales_history = []
sale_counter = 0

def get_product_by_id(product_id):
    """Helper function to find a product by its ID."""
    for product in products:
        if product['id'] == product_id:
            return product
    return None

def calculate_cart_total(cart):
    """Calculates the total price of all items in the cart."""
    total = sum(item['price'] * item['quantity'] for item in cart)
    return total

def index(request):
    """Renders the main page with the product list and cart."""
    # Initialize an empty cart in the session if it doesn't exist
    if 'cart' not in request.session:
        request.session['cart'] = []
    
    context = {
        'products': products,
        'cart': request.session.get('cart', []),
        'cart_total': calculate_cart_total(request.session.get('cart', [])),
        'sales_history': sales_history,
    }
    return render(request, 'pos/cart.html', context)

def add_to_cart(request):
    """Handles AJAX requests to add a product to the cart."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = int(data.get('product_id'))
            
            product = get_product_by_id(product_id)
            if not product:
                return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)

            cart = request.session.get('cart', [])
            item_found = False
            for item in cart:
                if item['id'] == product_id:
                    item['quantity'] += 1
                    item_found = True
                    break
            
            if not item_found:
                new_item = {
                    'id': product['id'],
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': 1,
                }
                cart.append(new_item)

            request.session['cart'] = cart
            
            cart_total = calculate_cart_total(cart)
            
            return JsonResponse({'success': True, 'cart': cart, 'cart_total': cart_total})
            
        except (json.JSONDecodeError, ValueError, KeyError):
            return JsonResponse({'success': False, 'error': 'Invalid request data'}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def update_cart_quantity(request):
    """Handles AJAX requests to update a product's quantity in the cart."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = int(data.get('product_id'))
            new_quantity = int(data.get('quantity'))

            cart = request.session.get('cart', [])
            
            # Find the item in the cart and update its quantity
            item_to_update = None
            for item in cart:
                if item['id'] == product_id:
                    item_to_update = item
                    break
            
            if item_to_update:
                if new_quantity > 0:
                    item_to_update['quantity'] = new_quantity
                else:
                    # Remove the item if quantity is 0 or less
                    cart.remove(item_to_update)
            
            request.session['cart'] = cart
            request.session.modified = True
            
            cart_total = calculate_cart_total(cart)
            
            return JsonResponse({'success': True, 'cart': cart, 'cart_total': cart_total})
        
        except (json.JSONDecodeError, ValueError, KeyError):
            return JsonResponse({'success': False, 'error': 'Invalid request data'}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def checkout(request):
    """Handles the checkout process and saves the sale."""
    global sale_counter
    if request.method == 'POST':
        cart = request.session.get('cart', [])
        if not cart:
            return JsonResponse({'success': False, 'error': 'Cart is empty'}, status=400)
            
        cart_copy = [item.copy() for item in cart]
        sale_counter += 1
        sale_record = {
            'id': sale_counter,
            'items': cart_copy,
            'total': calculate_cart_total(cart),
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        print(calculate_cart_total(cart))
        my_sales = Sale(items=cart_copy, total=calculate_cart_total(cart))
        my_sales.save()
        
        sales_history.append(sale_record)
        
        request.session['cart'] = []
        request.session.modified = True
        
        return JsonResponse({'success': True, 'message': 'Checkout successful. Your order has been placed!', 'sales_history': sales_history})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
