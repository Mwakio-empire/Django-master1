from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, ProductImage, Comment, DeliveryContact, Order
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


# Register DeliveryContact model
@admin.register(DeliveryContact)
class DeliveryContactAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone_number', 'available')
    search_fields = ('username', 'phone_number')
    list_filter = ('available',)
    
    
# Update the OrderAdmin to show delivery contact
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'created_at', 'delivery_contact')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__username')
    ordering = ('-created_at',)

    # Include delivery contact when displaying order info
    def delivery_contact(self, obj):
        if obj.delivery_contact:
            return f"{obj.delivery_contact.username} ({obj.delivery_contact.phone_number})"
        return "No delivery contact assigned"

# Register Comment model
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    search_fields = ('user__username', 'product__name', 'text')
    list_filter = ('rating', 'created_at')

# Register Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Register ProductImage model
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('image_thumbnail', 'description')
    list_display_links = ('image_thumbnail',)
    search_fields = ('description',)

    def image_thumbnail(self, obj):
        return format_html('<img src="{}" width="100" />', obj.image.url)
    image_thumbnail.short_description = 'Image'

# Define inline for ProductImage
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

# Register Product model with inline ProductImage
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('id', 'name', 'price', 'category', 'is_featured', 'available', 'main_image_thumbnail')
    list_filter = ('category', 'is_featured', 'available')
    search_fields = ('name', 'description')
    ordering = ('-price',)

    def main_image_thumbnail(self, obj):
        return format_html('<img src="{}" width="100" />', obj.main_image.url)
    main_image_thumbnail.short_description = 'Main Image'




class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
