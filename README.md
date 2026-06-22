# E-Commerce Application

A complete Django 4+ e-commerce application with Razorpay payment integration.

## Features

- Product listing and detail pages
- Add to cart and buy now functionality
- Cart management (update quantity, remove items)
- Checkout with Razorpay payment
- Order creation after successful payment
- Support for authenticated and guest users (session-based cart)
- Stock management with safety checks

## Tech Stack

- Python 3.10+
- Django 4+
- SQLite
- Razorpay (Test Mode)
- Bootstrap 5

## Setup

1. Clone or download the project.

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Apply migrations:
   ```
   python manage.py migrate
   ```

4. Create superuser:
   ```
   python manage.py createsuperuser
   ```

5. Configure Razorpay keys in `ecommerce/settings.py`:
   ```python
   RAZORPAY_KEY_ID = 'your_test_key_id'
   RAZORPAY_KEY_SECRET = 'your_test_secret'
   ```

6. Run the server:
   ```
   python manage.py runserver
   ```

7. Access the application at `http://127.0.0.1:8000/`

## Usage

- Browse products on the home page
- View product details
- Add items to cart or buy now
- Manage cart
- Proceed to checkout and pay with Razorpay test mode
- Admin panel at `/admin/` for managing products

## Security Notes

- Never trust frontend amounts; always recalculate on server
- Razorpay signature verification is mandatory
- Stock is safely reduced using database transactions
- Session-based carts for guest users

## Models

- **Product**: Name, description, price, stock, image
- **Cart**: User or session-based cart
- **CartItem**: Items in cart
- **Order**: Order details with Razorpay info
- **OrderItem**: Items in order

## Views

- Product listing and detail
- Cart management
- Checkout and payment processing
- Payment success/failure handling

## Templates

- Base template with Bootstrap
- Product list and detail
- Cart and checkout
- Payment success/failure pages