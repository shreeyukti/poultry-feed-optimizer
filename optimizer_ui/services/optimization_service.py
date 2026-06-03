import pandas as pd
import pulp

from core.optimizers import PulpFeedOptimizer
from core.reporter import generate_report
from core.validator import validate_data
from optimizer_ui.models import (
    OptimizationResultItem,
    OptimizationRun,
    OptimizationIngredientSnapshot,
    OptimizationNutrientSnapshot,
)
from optimizer_ui.services.dataframe_loader import load_optimization_dataframes


class OptimizationService:
    def __init__(self, optimizer=None):
        self.optimizer = optimizer or PulpFeedOptimizer()

    def optimize_formula(self, formula):
        ingredients_df, constraints_df = load_optimization_dataframes(
            formula=formula
        )

        errors, warnings = validate_data(ingredients_df, constraints_df)

        if errors:
            return {
                "status": "Validation Error",
                "errors": errors,
                "warnings": warnings,
            }

        ingredients_df["cost"] = pd.to_numeric(
            ingredients_df["cost"],
            errors="coerce"
        )

        ingredients_df["minquantity"] = pd.to_numeric(
            ingredients_df["minquantity"],
            errors="coerce"
        ).fillna(0)

        ingredients_df["maxquantity"] = pd.to_numeric(
            ingredients_df["maxquantity"],
            errors="coerce"
        )

        active_ingredients = ingredients_df[
            (ingredients_df["cost"].notna()) &
            (ingredients_df["cost"] > 0) &
            ~(
                (ingredients_df["minquantity"] == 0) &
                (ingredients_df["maxquantity"].isna())
            )
        ]

        model, quantity, constraints_df = self.optimizer.optimize(
            active_ingredients,
            constraints_df,
        )

        status = pulp.LpStatus[model.status]

        if status != "Optimal":
            return {
                "status": status,
                "warnings": warnings,
                "total_cost": "No valid solution found",
            }

        report = generate_report(
            model,
            quantity,
            active_ingredients,
            constraints_df,
        )

        previous_run = (
            OptimizationRun.objects
            .filter(formula=formula, status="Optimal")
            .order_by("-created_at")
            .first()
        )

        optimization_run = OptimizationRun.objects.create(
            formula=formula,
            total_weight=1000,
            total_cost=report["total_cost"],
            status=status,
        )

        for item in report["ingredients"]:
            ingredient_obj = formula.ingredients.get(ingredient=item["name"])

            OptimizationResultItem.objects.create(
                run=optimization_run,
                ingredient=ingredient_obj,
                quantity=item["quantity"],
                cost_contribution=item["total_cost"],
            )

            OptimizationIngredientSnapshot.objects.create(
                run=optimization_run,
                ingredient_name=item["name"],
                solution_kg=item.get("quantity"),
                cost_per_kg=item.get("cost_per_kg"),
                total_cost=item.get("total_cost"),
                minquantity=item.get("minquantity"),
                maxquantity=item.get("maxquantity"),
            )

        for nutrient in report["nutrients"]:
            OptimizationNutrientSnapshot.objects.create(
                run=optimization_run,
                nutrient_name=nutrient.get("name"),
                actual_value=nutrient.get("achieved"),
                min_value=nutrient.get("min"),
                max_value=nutrient.get("max"),
            )

        result = {
            "status": status,
            "warnings": warnings,
            "saved_run": optimization_run,
            "total_cost": report["total_cost"],
            "optimized_ingredients": report["ingredients"],
            "achieved_nutrients": report["nutrients"],
        }

        if previous_run:
            cost_difference = (
                optimization_run.total_cost - previous_run.total_cost
            )
            cost_difference_percentage = (
                cost_difference / previous_run.total_cost * 100
            )

            result.update({
                "previous_cost": round(previous_run.total_cost, 3),
                "cost_difference": round(cost_difference, 3),
                "cost_difference_percentage": round(
                    cost_difference_percentage,
                    2,
                ),
            })

        return result