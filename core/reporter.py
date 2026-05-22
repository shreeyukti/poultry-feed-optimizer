import pulp
import pandas as pd


def generate_report(model, quantity, ingredients, constraints):
    rows = []

    for name, var in quantity.items():
        optimized_qty = var.value()

        if optimized_qty is None:
            optimized_qty = 0

        ingredient_row = ingredients[ingredients["ingredient"] == name].iloc[0]
        cost = ingredient_row["cost"]

        rows.append({
            "Ingredient": name,
            "Optimised Quantity": round(optimized_qty, 3),
            "cost per kg": round(cost, 3),
            "Total cost": round(optimized_qty * cost, 3)
        })

    report_df = pd.DataFrame(rows)
    used_dataframe = report_df[report_df["Optimised Quantity"] > 0]

    print("\nOPTIMISED INGREDIENT QUANTITY:")
    print(used_dataframe.to_string(index=False))

    print("\nTOTAL SUMMARY:")
    print("total quantity:", round(report_df["Optimised Quantity"].sum(), 3))
    print("total cost:", round(pulp.value(model.objective), 3))

    print("\nACHIEVED NUTRIENTS:")

    nutrient_rows = []

    for index, row in constraints.iterrows():
        nutrient = row["nutrient"]

        if nutrient not in ingredients.columns:
            continue

        nutrient_total = 0

        for i, ingredient_row in ingredients.iterrows():
            ing_name = ingredient_row["ingredient"]
            qty = quantity[ing_name].value()

            if qty is None:
                qty = 0

            nutrient_value = ingredient_row[nutrient]

            if pd.isna(nutrient_value):
                nutrient_value = 0

            nutrient_total += nutrient_value * qty

        achieved_value = nutrient_total / 1000

        nutrient_rows.append({
            "Nutrient": nutrient,
            "Achieved Value": round(achieved_value, 4),
            "Min Required": row["min"],
            "Max Allowed": row["max"]
        })

    nutrient_df = pd.DataFrame(nutrient_rows)
    print(nutrient_df.to_string(index=False))

    report_df.to_csv("optiimised_result.csv", index=False)
    nutrient_df.to_csv("achieved_nutrients.csv", index=False)

    return report_df,nutrient_df