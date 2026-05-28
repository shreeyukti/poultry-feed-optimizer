from django.contrib import admin
from .models import (Company,Plant,Formula,Ingredient,Nutrient,IngredientNutrient,NutrientConstraint,OptimizationRun,OptimizationResultItem,)


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




@admin.register(NutrientConstraint)
class NutrientConstraintAdmin(admin.ModelAdmin):
    list_display = ("formula", "nutrient", "min_value", "max_value")
    list_filter = ("formula", "nutrient")
    search_fields = ("nutrient__name", "formula__name")



admin.site.register(Formula)
admin.site.register(Plant)
admin.site.register(Company)
admin.site.register(OptimizationRun)
admin.site.register(OptimizationResultItem)