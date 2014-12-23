# coding=utf-8
from django.contrib import admin
from .models import Shop, OrderLog, Order, OrderProduct, Category, Product, Icon


class ProductAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_filter = ["shop", "category"]
    list_display = ["name", "attr", "simple_introduction_top", "price", "unit", "status"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        print db_field
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(parent_category__isnull=False)
        if db_field.name == "parent_product":
            kwargs["queryset"] = Product.objects.filter(is_virtual=True)
        return super(ProductAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class CategoryAdmin(admin.ModelAdmin):
    list_filter = ["shop"]
    list_display = ["name", "shop"]


class OrderAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "address"]

admin.site.register(Shop)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLog)
admin.site.register(OrderProduct)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Icon)