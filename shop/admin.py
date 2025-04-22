from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import AdminSite
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import (
    Customer, CustomerVerification, CustomerPasswordReset,
    Category, Product, Review, Order, OrderItem, Promotion
)

class ElectronicsShopAdmin(AdminSite):
    site_header = 'Royal Tech Kutus'
    site_title = 'Royal Tech Kutus Admin Portal'
    index_title = 'Welcome to Royal Tech Kutus Admin Portal'
    
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        app_order = {
            'shop': 1,
            'registration': 2,
        }
        app_list.sort(key=lambda x: app_order.get(x['app_label'], 10))
        return app_list

admin_site = ElectronicsShopAdmin(name='electronics_admin')

# Customer Authentication Admin
class CustomerVerificationInline(admin.TabularInline):
    model = CustomerVerification
    extra = 0
    readonly_fields = ('token', 'created_at', 'expires_at')

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_verified')
    list_filter = ('is_active', 'is_verified')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    inlines = [CustomerVerificationInline]

admin_site.register(Customer, CustomerAdmin)

# Shop Admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ['get_product_info', 'category', 'price', 'stock', 'get_status', 'created']
    list_filter = ['available', 'created', 'category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    exclude = ['created_by', 'updated_by']

    def get_product_info(self, obj):
        if obj.image:
            return format_html(
                '<div style="display: flex; align-items: center;">'
                '<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px; margin-right: 10px;">'
                '<div>'
                '<div style="font-weight: 600;">{}</div>'
                '<div style="color: #666; font-size: 0.9em;">{}</div>'
                '</div>'
                '</div>',
                obj.image.url,
                obj.name,
                obj.category.name
            )
        return obj.name
    get_product_info.short_description = 'Product'

    def get_status(self, obj):
        if obj.available:
            return format_html(
                '<span class="status-tag status-completed">In Stock</span>'
            )
        return format_html(
            '<span class="status-tag status-pending">Out of Stock</span>'
        )
    get_status.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

admin_site.register(Product, ProductAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    exclude = ['created_by']

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

admin_site.register(Category, CategoryAdmin)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'rating', 'created', 'is_approved')
    list_filter = ('rating', 'is_approved', 'created')
    search_fields = ('product__name', 'customer__username', 'comment')
    raw_id_fields = ('product', 'customer')
    exclude = ['approved_by']

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('is_approved') and not obj.approved_by:
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)

admin_site.register(Review, ReviewAdmin)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    readonly_fields = ['get_product_info', 'price', 'quantity', 'get_total']
    fields = ['get_product_info', 'quantity', 'price', 'get_total']
    can_delete = False
    max_num = 0
    extra = 0
    
    def get_product_info(self, obj):
        if not obj.product:
            return "Product not available"
        if obj.product.image:
            return format_html(
                '<div style="display: flex; align-items: center;">'
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; margin-right: 10px;">'
                '<span>{}</span>'
                '</div>',
                obj.product.image.url,
                obj.product.name
            )
        return obj.product.name
    get_product_info.short_description = 'Product'
    
    def get_total(self, obj):
        if obj.price is None or obj.quantity is None:
            return "N/A"
        total = float(obj.price) * int(obj.quantity)
        return format_html("KSh {}", total)
    get_total.short_description = 'Total'

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_customer_info', 'get_order_details', 'get_total_cost', 'get_status', 'created']
    list_filter = ['status', 'created', 'updated', 'paid']
    search_fields = ['first_name', 'last_name', 'phone_number', 'email', 'location',
                    'customer__username', 'customer__email']
    readonly_fields = ['get_total_cost', 'created', 'updated']
    raw_id_fields = ['customer']
    exclude = ['processed_by']
    inlines = [OrderItemInline]

    def get_customer_info(self, obj):
        return format_html(
            '<div style="min-width: 200px;">'
            '<div style="font-weight: 600;">{} {}</div>'
            '<div style="color: #666; font-size: 0.9em;">{}</div>'
            '</div>',
            obj.first_name, obj.last_name,
            obj.email or 'No email'
        )
    get_customer_info.short_description = 'Customer'

    def get_order_details(self, obj):
        return format_html(
            '<div style="min-width: 200px;">'
            '<div style="font-weight: 600;">Order #{}</div>'
            '<div style="color: #666; font-size: 0.9em;">{} items</div>'
            '</div>',
            obj.id,
            obj.items.count()
        )
    get_order_details.short_description = 'Order Details'

    def get_status(self, obj):
        status_classes = {
            'pending': 'status-pending',
            'processing': 'status-processing',
            'shipped': 'status-shipped',
            'delivered': 'status-completed',
            'cancelled': 'status-cancelled'
        }
        return format_html(
            '<span class="status-tag {}">{}</span>',
            status_classes.get(obj.status, 'status-default'),
            obj.get_status_display()
        )
    get_status.short_description = 'Status'

    def get_total_cost(self, obj):
        return format_html("KSh {}", obj.get_total_cost())
    get_total_cost.short_description = 'Total Cost'

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.processed_by = request.user
        super().save_model(request, obj, form, change)

admin_site.register(Order, OrderAdmin)

class CustomerPasswordResetAdmin(admin.ModelAdmin):
    list_display = ['customer', 'created_at', 'expires_at', 'is_used']
    list_filter = ['is_used', 'created_at']
    search_fields = ['customer__username', 'customer__email', 'token']
    readonly_fields = ['token', 'created_at', 'expires_at']

admin_site.register(CustomerPasswordReset, CustomerPasswordResetAdmin)

class PromotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'is_active', 'start_date', 'end_date']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    date_hierarchy = 'start_date'
    ordering = ['-created_at']

admin_site.register(Promotion, PromotionAdmin)
