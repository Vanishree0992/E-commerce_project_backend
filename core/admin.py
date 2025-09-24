from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product

# ---------------------------
# Subcategory Inline for CategoryAdmin
# ---------------------------
class SubCategoryInline(admin.TabularInline):
    model = Category
    fk_name = 'parent'
    extra = 1
    verbose_name = "Subcategory"
    verbose_name_plural = "Subcategories"

# ---------------------------
# Category Admin
# ---------------------------
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    inlines = [SubCategoryInline]

# ---------------------------
# Product Admin
# ---------------------------
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'price', 'discount_price', 'stock', 'rating',
        'category', 'size', 'color', 'is_available', 'image_tag', 'created_at', 'updated_at'
    )
    list_filter = ('category', 'size', 'color', 'is_available')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name', 'category')

    # Show image thumbnail
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Image'

# ---------------------------
# Register Admin Models
# ---------------------------
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
