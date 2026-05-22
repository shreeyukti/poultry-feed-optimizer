from django.shortcuts import render
import pulp

from config import INGREDIENTS_FILE, CONSTRAINTS_FILE
from core.loader import load_csv
from core.validator import validate_data
from core.optimizer import run_optimization
from core.reporter import generate_report


def home(request):
    context = {}

    if request.method == "POST":
        ingredients = load_csv(INGREDIENTS_FILE)
        constraints = load_csv(CONSTRAINTS_FILE)

        errors, warnings = validate_data(ingredients, constraints)

        if errors:
            context["status"] = "Validation Error"
            context["total_cost"] = errors

        else:
            active_ingredients = ingredients[ingredients["cost"].notna() & (ingredients["cost"] > 0)]
            model, quantity, constraints = run_optimization(active_ingredients,constraints)
            status = pulp.LpStatus[model.status]
            context["status"] = status

            if status == "Optimal":
                total_cost = pulp.value(model.objective)
                context["total_cost"] = round(total_cost, 3)

                ingredient_results = []

                for name, var in quantity.items():
                    qty = var.value()

                    if qty is not None and qty > 0:
                        ingredient_results.append({"name": name,"quantity": round(qty, 3)})

                report_df, nutrient_df = generate_report(model,quantity,active_ingredients,constraints)

                ingredient_rows = []

                used_df = report_df[report_df["Optimised Quantity"] > 0]

                for _, row in used_df.iterrows():
                    ingredient_rows.append({"name": row["Ingredient"],"quantity": row["Optimised Quantity"],})
                nutrient_rows = []
                for _, row in nutrient_df.iterrows():
                    nutrient_rows.append({"name": row["Nutrient"],"achieved": row["Achieved Value"],"min": row["Min Required"],"max": row["Max Allowed"],})
                context["ingredients"] = ingredient_rows
                context["nutrients"] = nutrient_rows
                             
            else:
                context["total_cost"] = "No valid solution found"

    return render(request, "optimizer_ui/home.html", context)