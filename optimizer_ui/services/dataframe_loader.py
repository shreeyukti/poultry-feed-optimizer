import pandas as pd

from optimizer_ui.models import Ingredient, Nutrient, NutrientConstraint


def _normalize_nutrient_name(name):
    return name.strip().lower()


def load_optimization_dataframes():
    """Convert relational formulation data into the tabular optimizer input."""
    nutrients = list(Nutrient.objects.order_by("name").values_list("name", flat=True))
    nutrient_columns = [_normalize_nutrient_name(name) for name in nutrients]
    ingredient_columns = [
        "ingredient",
        "cost",
        "minquantity",
        "maxquantity",
        *nutrient_columns,
    ]

    ingredient_rows = []
    ingredient_queryset = Ingredient.objects.prefetch_related(
        "nutrient_values__nutrient"
    ).order_by("ingredient")

    for ingredient in ingredient_queryset:
        row = {
            "ingredient": ingredient.ingredient,
            "cost": ingredient.cost,
            "minquantity": ingredient.minquantity,
            "maxquantity": ingredient.maxquantity,
        }
        for nutrient_value in ingredient.nutrient_values.all():
            nutrient_name = _normalize_nutrient_name(nutrient_value.nutrient.name)
            row[nutrient_name] = nutrient_value.value
        ingredient_rows.append(row)

    ingredients = pd.DataFrame(ingredient_rows, columns=ingredient_columns)

    constraint_rows = [
        {
            "nutrient": _normalize_nutrient_name(constraint.nutrient.name),
            "min": constraint.min,
            "max": constraint.max,
        }
        for constraint in (
            NutrientConstraint.objects.select_related("nutrient")
            .exclude(min__isnull=True, max__isnull=True)
            .order_by("nutrient__name")
        )
    ]
    constraints = pd.DataFrame(constraint_rows, columns=["nutrient", "min", "max"])

    return ingredients, constraints
