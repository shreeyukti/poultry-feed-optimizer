from django.contrib import admin
from .models import Ingredient, Nutrient, IngredientNutrient, NutrientConstraint


class IngredientNutrientInline(admin.TabularInline):
    model = IngredientNutrient
    extra = 3


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "cost", "minquantity", "maxquantity")
    inlines = [IngredientNutrientInline]


@admin.register(Nutrient)
class NutrientAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(IngredientNutrient)
class IngredientNutrientAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "nutrient", "value")


@admin.register(NutrientConstraint)
class NutrientConstraintAdmin(admin.ModelAdmin):
    list_display = ("nutrient", "min", "max")