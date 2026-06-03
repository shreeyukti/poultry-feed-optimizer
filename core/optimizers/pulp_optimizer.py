import pandas as pd
import pulp

from .base import BaseFeedOptimizer


class PulpFeedOptimizer(BaseFeedOptimizer):
    def optimize(self, ingredients, constraints):
        model = pulp.LpProblem("feed_optimization", pulp.LpMinimize)
        quantity = {}

        for _, row in ingredients.iterrows():
            name = row["ingredient"]
            min_qty = row["minquantity"]
            max_qty = row["maxquantity"]

            if pd.isna(min_qty):
                min_qty = 0

            if pd.isna(max_qty):
                max_qty = None

            quantity[name] = pulp.LpVariable(
                name,
                lowBound=min_qty,
                upBound=max_qty,
            )

        model += pulp.lpSum(
            quantity[row["ingredient"]] * row["cost"]
            for _, row in ingredients.iterrows()
        )
        model += pulp.lpSum(quantity.values()) == 1000

        for _, row in constraints.iterrows():
            nutrient = row["nutrient"]
            min_value = row["min"]
            max_value = row["max"]

            if nutrient not in ingredients.columns:
                continue

            nutrient_total = pulp.lpSum(
                quantity[ingredient_row["ingredient"]]
                * (
                    0
                    if pd.isna(ingredient_row[nutrient])
                    else ingredient_row[nutrient]
                )
                for _, ingredient_row in ingredients.iterrows()
            )

            if not pd.isna(min_value):
                model += nutrient_total >= min_value * 1000

            if not pd.isna(max_value):
                model += nutrient_total <= max_value * 1000

        model.solve(pulp.PULP_CBC_CMD(msg=False))

        return model, quantity, constraints
