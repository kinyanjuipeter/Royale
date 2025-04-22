import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electronics_shop.settings')
django.setup()

from shop.models import Category, Product

def populate():
    # Create categories
    laptops = Category.objects.create(
        name='Laptops',
        slug='laptops',
        description='High-performance laptops for all needs'
    )
    
    smartphones = Category.objects.create(
        name='Smartphones',
        slug='smartphones',
        description='Latest smartphones with great features'
    )
    
    accessories = Category.objects.create(
        name='Accessories',
        slug='accessories',
        description='Various electronics accessories'
    )
    
    # Create products
    Product.objects.create(
        category=laptops,
        name='MacBook Pro 16"',
        slug='macbook-pro-16',
        description='Apple MacBook Pro with M2 Pro chip, 16-core GPU, 32GB RAM, 1TB SSD',
        price=249999,
        old_price=279999,
        stock=10,
        brand='Apple'
    )
    
    Product.objects.create(
        category=laptops,
        name='Dell XPS 15',
        slug='dell-xps-15',
        description='Powerful Windows laptop with 4K OLED display, Intel i9, 32GB RAM',
        price=189999,
        old_price=209999,
        stock=15,
        brand='Dell'
    )
    
    Product.objects.create(
        category=smartphones,
        name='iPhone 15 Pro',
        slug='iphone-15-pro',
        description='Latest iPhone with A17 Pro chip, 6.1" Super Retina XDR display',
        price=159999,
        old_price=179999,
        stock=20,
        brand='Apple'
    )
    
    Product.objects.create(
        category=smartphones,
        name='Samsung Galaxy S23 Ultra',
        slug='samsung-galaxy-s23-ultra',
        description='Flagship Android smartphone with 200MP camera, S Pen support',
        price=149999,
        old_price=169999,
        stock=18,
        brand='Samsung'
    )
    
    Product.objects.create(
        category=accessories,
        name='AirPods Pro (2nd Gen)',
        slug='airpods-pro-2',
        description='Premium wireless earbuds with ANC and spatial audio',
        price=34999,
        old_price=39999,
        stock=30,
        brand='Apple'
    )
    
    print("Database populated with sample data!")

if __name__ == '__main__':
    populate()
