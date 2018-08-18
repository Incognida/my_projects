from django.contrib import admin
from .models import Event, Category, Subcategory


@admin.register(Event)
class EventModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Subcategory)
class SubcategoryModelAdmin(admin.ModelAdmin):
    pass
