import pulp
import pandas as pd

from core.optimizer import run_optimization

INGREDIENT_STEP_KG = 1
NUTRIENT_STEP_PERCENT = 1


def is_binding(value, bound, tolerance=0.001):
    if pd.isna(value) or pd.isna(bound):
        return False

    return abs(float(value) - float(bound)) <= tolerance


def solve_modified_cost(ingredients, constraints):
    try:
        new_model, _, _ = run_optimization(ingredients, constraints)
        status = pulp.LpStatus[new_model.status]

        if status != "Optimal":
            return None

        return pulp.value(new_model.objective)

    except Exception:
        return None


def generate_report(model, quantity, ingredients, constraints):
    base_total_cost = pulp.value(model.objective)

    ingredient_rows = []

    for name, var in quantity.items():
        optimized_qty = var.value() or 0

        ingredient_row = ingredients[
            ingredients["ingredient"] == name
        ].iloc[0]

        cost = ingredient_row["cost"]

        sensitivity = ""
        cost_difference_for_change = None

        minquantity = ingredient_row["minquantity"]
        maxquantity = ingredient_row["maxquantity"]

        if (
            pd.notna(minquantity)
            and is_binding(optimized_qty, minquantity)
            and minquantity > 0
        ):
            sensitivity = "MIN ↓"

            modified_ingredients = ingredients.copy()

            ingredient_index = modified_ingredients[
                modified_ingredients["ingredient"] == name
            ].index[0]

            modified_ingredients.at[
                ingredient_index,
                "minquantity"
            ] = max(
                0,
                minquantity - INGREDIENT_STEP_KG
            )

            new_cost = solve_modified_cost(
                modified_ingredients,
                constraints.copy()
            )

            if new_cost is not None:
                cost_difference_for_change = round(
                    new_cost - base_total_cost,
                    3
                )

        elif (
            pd.notna(maxquantity)
            and is_binding(optimized_qty, maxquantity)
        ):
            sensitivity = "MAX ↑"

            modified_ingredients = ingredients.copy()

            ingredient_index = modified_ingredients[
                modified_ingredients["ingredient"] == name
            ].index[0]

            modified_ingredients.at[
                ingredient_index,
                "maxquantity"
            ] = (
                maxquantity + INGREDIENT_STEP_KG
            )

            new_cost = solve_modified_cost(
                modified_ingredients,
                constraints.copy()
            )

            if new_cost is not None:
                cost_difference_for_change = round(
                    new_cost - base_total_cost,
                    3
                )

        ingredient_rows.append({
            "name": name,
            "quantity": round(optimized_qty, 3),
            "minquantity": minquantity,
            "maxquantity": maxquantity,
            "cost_per_kg": round(cost, 3),
            "total_cost": round(
                optimized_qty * cost,
                3
            ),
            "sensitivity": sensitivity,
            "cost_difference_for_change":
                cost_difference_for_change,
        })

    used_ingredients = [
        row for row in ingredient_rows
        if row["quantity"] > 0
    ]

    nutrient_rows = []

    for _, row in constraints.iterrows():
        nutrient = row["nutrient"]

        if nutrient not in ingredients.columns:
            continue

        nutrient_total = 0

        for _, ingredient_row in ingredients.iterrows():
            ing_name = ingredient_row["ingredient"]

            qty = quantity[ing_name].value() or 0

            nutrient_value = ingredient_row[nutrient]

            if pd.isna(nutrient_value):
                nutrient_value = 0

            nutrient_total += (
                nutrient_value * qty
            )

        achieved_value = nutrient_total / 1000

        sensitivity = ""
        cost_difference_for_change = None

        min_value = row["min"]
        max_value = row["max"]

        # ---------------- MIN SENSITIVITY ---------------- #

        if (
            pd.notna(min_value)
            and is_binding(
                achieved_value,
                min_value
            )
            and min_value > 0
        ):
            sensitivity = "MIN ↓"

            modified_constraints = constraints.copy()

            constraint_index = modified_constraints[
                modified_constraints["nutrient"]
                == nutrient
            ].index[0]

            # REDUCE BY 1%
            modified_constraints.at[
                constraint_index,
                "min"
            ] = max(
                0,
                min_value - (
                    min_value
                    * NUTRIENT_STEP_PERCENT
                    / 100
                )
            )

            new_cost = solve_modified_cost(
                ingredients.copy(),
                modified_constraints
            )

            if new_cost is not None:
                cost_difference_for_change = round(
                    new_cost - base_total_cost,
                    3
                )

        # ---------------- MAX SENSITIVITY ---------------- #

        elif (
            pd.notna(max_value)
            and is_binding(
                achieved_value,
                max_value
            )
        ):
            sensitivity = "MAX ↑"

            modified_constraints = constraints.copy()

            constraint_index = modified_constraints[
                modified_constraints["nutrient"]
                == nutrient
            ].index[0]

            # INCREASE BY 1%
            modified_constraints.at[
                constraint_index,
                "max"
            ] = (
                max_value + (
                    max_value
                    * NUTRIENT_STEP_PERCENT
                    / 100
                )
            )

            new_cost = solve_modified_cost(
                ingredients.copy(),
                modified_constraints
            )

            if new_cost is not None:
                cost_difference_for_change = round(
                    new_cost - base_total_cost,
                    3
                )

        nutrient_rows.append({
            "name": nutrient,
            "achieved": round(
                achieved_value,
                4
            ),
            "min": min_value,
            "max": max_value,
            "sensitivity": sensitivity,
            "cost_difference_for_change":
                cost_difference_for_change,
        })

    total_cost = round(
        base_total_cost,
        3
    )

    return {
        "total_cost": total_cost,
        "ingredients": used_ingredients,
        "nutrients": nutrient_rows
    }

