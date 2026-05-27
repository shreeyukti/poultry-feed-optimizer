import pandas as pd

from optimizer_ui.models import Nutrient


def _normalize_nutrient_name(name):
    return name.strip().lower()


def load_optimization_dataframes(formula=None):
    """
    Convert relational formulation data into tabular optimizer input.

    If formula is provided, load only:
    - ingredients under that formula
    - nutrient constraints under that formula
    """

    if formula is None:
        raise ValueError("formula is required. Load data for one selected formula only.")

    nutrients = list(
        Nutrient.objects.order_by("name").values_list("name", flat=True)
    )
    nutrient_columns = [_normalize_nutrient_name(name) for name in nutrients]

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