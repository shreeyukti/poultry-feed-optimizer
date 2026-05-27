from django.shortcuts import render,  get_object_or_404
import pulp

from core.validator import validate_data
from core.optimizer import run_optimization
from core.reporter import generate_report
from .services.dataframe_loader import load_optimization_dataframes
from .models import Plant, Formula


def home(request):
     return render(request, "optimizer_ui/home.html", {
        "status": "Use plant and formula pages to run optimization."
    })


def plant_list(request):
    plants = Plant.objects.select_related("company").all().order_by(
        "company__name",
        "name"
    )

    return render(request, "optimizer_ui/plant_list.html", {
        "plants": plants,
    })


def formula_list(request, plant_id):
    plant = get_object_or_404(
        Plant.objects.select_related("company"),
        id=plant_id
    )

    formulas = Formula.objects.filter(plant=plant).order_by("name")

    return render(request, "optimizer_ui/formula_list.html", {
        "plant": plant,
        "formulas": formulas,
    })


def formula_detail(request, formula_id):
    formula = get_object_or_404(
        Formula.objects.select_related("plant", "plant__company"),
        id=formula_id
    )

    ingredients = (
        formula.ingredients
        .prefetch_related("nutrient_values__nutrient")
        .order_by("ingredient")
    )

    nutrient_constraints = (
        formula.nutrient_constraints
        .select_related("nutrient")
        .order_by("nutrient__name")
    )

    context = {
        "formula": formula,
        "plant": formula.plant,
        "ingredients": ingredients,
        "nutrient_constraints": nutrient_constraints,
    }

    if request.method == "POST":
        ingredients_df, constraints_df = load_optimization_dataframes(formula=formula)

        errors, warnings = validate_data(ingredients_df, constraints_df)
        context["warnings"] = warnings

        if errors:
            context["status"] = "Validation Error"
            context["errors"] = errors
        else:
            active_ingredients = ingredients_df[
                ingredients_df["cost"].notna() & (ingredients_df["cost"] > 0)
            ]

            model, quantity, constraints_df = run_optimization(
                active_ingredients,
                constraints_df
            )

            status = pulp.LpStatus[model.status]
            context["status"] = status

            if status == "Optimal":
                report = generate_report(
                    model,
                    quantity,
                    active_ingredients,
                    constraints_df
                )

                context["total_cost"] = report["total_cost"]
                context["optimized_ingredients"] = report["ingredients"]
                context["achieved_nutrients"] = report["nutrients"]
            
            else:
                context["total_cost"] = "No valid solution found"
    return render(request, "optimizer_ui/formula_detail.html", context)