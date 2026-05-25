from django.shortcuts import render
import pulp

from core.validator import validate_data
from core.optimizer import run_optimization
from core.reporter import generate_report
from .services.dataframe_loader import load_optimization_dataframes


def home(request):
    context = {}

    if request.method == "POST":
        ingredients, constraints = load_optimization_dataframes()

        errors, warnings = validate_data(ingredients, constraints)
        context["warnings"] = warnings

        if errors:
            context["status"] = "Validation Error"
            context["errors"] = errors
            return render(request, "optimizer_ui/home.html", context)

        active_ingredients = ingredients[
            ingredients["cost"].notna() & (ingredients["cost"] > 0)
        ]

        model, quantity, constraints = run_optimization(
            active_ingredients,
            constraints
        )

        status = pulp.LpStatus[model.status]
        context["status"] = status

        if status == "Optimal":
            report = generate_report(
                model,
                quantity,
                active_ingredients,
                constraints
            )

            context["total_cost"] = report["total_cost"]
            context["ingredients"] = report["ingredients"]
            context["nutrients"] = report["nutrients"]

        else:
            context["total_cost"] = "No valid solution found"

    return render(request, "optimizer_ui/home.html", context)
