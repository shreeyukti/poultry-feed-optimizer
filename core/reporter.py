import pulp
import pandas as pd


def generate_report(model, quantity, ingredients, constraints):
    ingredient_rows = []

    for name, var in quantity.items():
        optimized_qty = var.value() or 0
        ingredient_row = ingredients[ingredients["ingredient"] == name].iloc[0]
        cost = ingredient_row["cost"]

        ingredient_rows.append({
            "name": name,
            "quantity": round(optimized_qty, 3),
            "minquantity": ingredient_row["minquantity"],
            "maxquantity": ingredient_row["maxquantity"],
            "cost_per_kg": round(cost, 3),
            "total_cost": round(optimized_qty * cost, 3)

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

            nutrient_total += nutrient_value * qty

        achieved_value = nutrient_total / 1000

        nutrient_rows.append({
            "name": nutrient,
            "achieved": round(achieved_value, 4),
            "min": row["min"],
            "max": row["max"]
        })

    total_cost = round(pulp.value(model.objective), 3)

    return {
        "total_cost": total_cost,
        "ingredients": used_ingredients,
        "nutrients": nutrient_rows
    }