from django.contrib import admin
from .models import product,cart,orders

# Register your models here.
class ProdAdmin(admin.ModelAdmin):
    list_display=['id','name','price','pdetails','cat','is_active']
    list_filter=['cat','is_active']
admin.site.register(product,ProdAdmin)
class cartAdmin(admin.ModelAdmin):
    list_display=['id','uid','pid']  
admin.site.register(cart,cartAdmin)
class OrderAdmin(admin.ModelAdmin):
    list_display=['id','order_id','uid','pid']  
admin.site.register(orders,OrderAdmin)


