from django import forms

from .models import (
    Ingredient,
    Formula,
    NutrientConstraint,
    Nutrient,
    IngredientNutrient,
    IngredientMaster,
    BaseIngredientNutrient,PlantIngredientNutrientOverlay
)



class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = [
            "ingredient_master",
            "cost",
            "minquantity",
            "maxquantity",
        ]


class FormulaForm(forms.ModelForm):
    class Meta:
        model = Formula
        fields = [
            "name"
        ]

class NutrientConstraintForm(forms.ModelForm):
    class Meta:
        model = NutrientConstraint
        fields = [
            "nutrient",
            "min_value",
            "max_value",
        ]

class NutrientForm(forms.ModelForm):
    class Meta:
        model = Nutrient
        fields = ["name", "unit"]

class IngredientNutrientForm(forms.ModelForm):
    class Meta:
        model = IngredientNutrient
        fields = ["nutrient", "value"]
    
class IngredientMasterForm(forms.ModelForm):
    class Meta:
        model = IngredientMaster
        fields = ["name", "description"]

class BaseIngredientNutrientForm(forms.ModelForm):
    class Meta:
        model = BaseIngredientNutrient
        fields = ["nutrient", "value"]

class PlantIngredientNutrientOverlayForm(forms.ModelForm):
    class Meta:
        model = PlantIngredientNutrientOverlay
        fields = [
            "ingredient_master",
            "nutrient",
            "value",
        ]