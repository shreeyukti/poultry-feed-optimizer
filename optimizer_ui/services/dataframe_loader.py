import pandas as pd

from optimizer_ui.models import Nutrient
from optimizer_ui.services.nutrition_service import NutritionService


def _normalize_nutrient_name(name):
    return name.strip().lower()


def load_optimization_dataframes(formula=None):
    """
    Convert relational formulation data into tabular optimizer input.

    Uses:
    - formula ingredients for cost/min/max
    - IngredientMaster connection for nutrient values
    - Plant-specific overlay if available
    - Base nutrient value if no overlay exists
    - Old IngredientNutrient values as fallback
    """

    if formula is None:
        raise ValueError("formula is required. Load data for one selected formula only.")

    plant = formula.plant

    nutrient_objects = list(Nutrient.objects.order_by("name"))
    nutrient_columns = [
        _normalize_nutrient_name(nutrient.name)
        for nutrient in nutrient_objects
    ]

    ingredient_columns = [
        "ingredient",
        "cost",
        "minquantity",
        "maxquantity",
        *nutrient_columns,
    ]

    ingredient_rows = []

    ingredient_queryset = (
        formula.ingredients
        .select_related("ingredient_master")
        .prefetch_related("nutrient_values__nutrient")
        .order_by("ingredient")
    )

    for ingredient in ingredient_queryset:
        row = {
            "ingredient": ingredient.ingredient,
            "cost": ingredient.cost,
            "minquantity": ingredient.minquantity,
            "maxquantity": ingredient.maxquantity,
        }

        # New architecture:
        # IngredientMaster -> Base nutrient values -> Plant overlay
        if ingredient.ingredient_master:
            for nutrient in nutrient_objects:
                nutrient_name = _normalize_nutrient_name(nutrient.name)

                row[nutrient_name] = NutritionService.get_effective_value(
                    plant=plant,
                    ingredient_master=ingredient.ingredient_master,
                    nutrient=nutrient,
                )

        # Old fallback:
        # Formula-specific IngredientNutrient values
        else:
            for nutrient_value in ingredient.nutrient_values.all():
                nutrient_name = _normalize_nutrient_name(
                    nutrient_value.nutrient.name
                )
                row[nutrient_name] = nutrient_value.value

        ingredient_rows.append(row)

    ingredients = pd.DataFrame(
        ingredient_rows,
        columns=ingredient_columns
    )

    constraint_rows = []

    constraint_queryset = (
        formula.nutrient_constraints
        .select_related("nutrient")
        .exclude(min_value__isnull=True, max_value__isnull=True)
        .order_by("nutrient__name")
    )

    for constraint in constraint_queryset:
        constraint_rows.append({
            "nutrient": _normalize_nutrient_name(constraint.nutrient.name),
            "min": constraint.min_value,
            "max": constraint.max_value,
        })

    constraints = pd.DataFrame(
        constraint_rows,
        columns=["nutrient", "min", "max"]
    )

    return ingredients, constraints