from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import (
    Plant,
    Formula,
    Ingredient,
    NutrientConstraint,
    OptimizationRun,Nutrient,
    IngredientNutrient,
    IngredientMaster,BaseIngredientNutrient,PlantIngredientNutrientOverlay
)
from .services.optimization_service import OptimizationService
from .forms import (
    IngredientForm,
    FormulaForm,
    NutrientConstraintForm,NutrientForm,IngredientNutrientForm,IngredientMasterForm,BaseIngredientNutrientForm,PlantIngredientNutrientOverlayForm
)


def login_view(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("optimizer_ui:dashboard")
        else:
            error = "Invalid username or password"

    return render(request, "optimizer_ui/login.html", {"error": error})


@login_required
def dashboard_view(request):
    total_plants = Plant.objects.filter(company__owner=request.user).count()
    total_formulas = Formula.objects.filter(plant__company__owner=request.user).count()
    total_runs = OptimizationRun.objects.filter(
        formula__plant__company__owner=request.user
    ).count()

    recent_runs = (
        OptimizationRun.objects
        .select_related("formula", "formula__plant", "formula__plant__company")
        .filter(formula__plant__company__owner=request.user)
        .order_by("-created_at")[:5]
    )

    return render(request, "optimizer_ui/dashboard.html", {
        "total_plants": total_plants,
        "total_formulas": total_formulas,
        "total_runs": total_runs,
        "recent_runs": recent_runs,
    })


@login_required
def logout_view(request):
    logout(request)
    return redirect("optimizer_ui:login")


@login_required
def home(request):
    return render(request, "optimizer_ui/home.html", {
        "status": "Use plant and formula pages to run optimization."
    })


@login_required
def plant_list(request):
    plants = (
        Plant.objects
        .select_related("company")
        .filter(company__owner=request.user)
        .order_by("company__name", "name")
    )

    return render(request, "optimizer_ui/plant_list.html", {
        "plants": plants,
    })


@login_required
def formula_list(request, plant_id):
    plant = get_object_or_404(
        Plant.objects.select_related("company"),
        id=plant_id,
        company__owner=request.user
    )

    formulas = Formula.objects.filter(plant=plant).order_by("name")

    return render(request, "optimizer_ui/formula_list.html", {
        "plant": plant,
        "formulas": formulas,
    })


@login_required
def formula_detail(request, formula_id):
    formula = get_object_or_404(
        Formula.objects.select_related("plant", "plant__company"),
        id=formula_id,
        plant__company__owner=request.user
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

        if "save_ingredients" in request.POST:
            for ingredient in ingredients:
                cost = request.POST.get(f"cost_{ingredient.id}")
                minquantity = request.POST.get(f"minquantity_{ingredient.id}")
                maxquantity = request.POST.get(f"maxquantity_{ingredient.id}")

                ingredient.cost = cost if cost != "" else None
                ingredient.minquantity = minquantity if minquantity != "" else 0
                ingredient.maxquantity = maxquantity if maxquantity != "" else None
                ingredient.save()

            return redirect("optimizer_ui:formula_detail", formula_id=formula.id)

        if "save_requirements" in request.POST:
            for constraint in nutrient_constraints:
                min_value = request.POST.get(f"min_{constraint.id}")
                max_value = request.POST.get(f"max_{constraint.id}")

                constraint.min_value = float(min_value) if min_value else None
                constraint.max_value = float(max_value) if max_value else None
                constraint.save()

            return redirect("optimizer_ui:formula_detail", formula_id=formula.id)

        if "optimize" in request.POST:
            context.update(
                OptimizationService().optimize_formula(formula)
            )

    optimized_by_name = {
        item["name"].lower(): item
        for item in context.get("optimized_ingredients", [])
    }

    ingredient_rows = []

    for ingredient in ingredients:
        item = optimized_by_name.get(ingredient.ingredient.lower())

        ingredient_rows.append({
            "obj": ingredient,
            "solution": item.get("quantity", "-") if item else "-",
            "price": item.get("cost_per_kg", ingredient.cost) if item else ingredient.cost,
            "total_cost": item.get("total_cost", "-") if item else "-",
            "minquantity": item.get("minquantity", ingredient.minquantity) if item else ingredient.minquantity,
            "maxquantity": item.get("maxquantity", ingredient.maxquantity) if item else ingredient.maxquantity,
            "sensitivity": item.get("sensitivity", "-") if item else "-",
            "cost_change": item.get("cost_difference_for_change", "-") if item else "-",
        })

    achieved_by_name = {
        item["name"].lower(): item
        for item in context.get("achieved_nutrients", [])
    }

    nutrient_rows = []

    for constraint in nutrient_constraints:
        item = achieved_by_name.get(constraint.nutrient.name.lower())

        nutrient_rows.append({
            "obj": constraint,
            "actual": item.get("achieved", "-") if item else "-",
            "min": item.get("min", constraint.min_value) if item else constraint.min_value,
            "max": item.get("max", constraint.max_value) if item else constraint.max_value,
            "sensitivity": item.get("sensitivity", "-") if item else "-",
            "cost_change": item.get("cost_difference_for_change", "-") if item else "-",
        })

    context["ingredient_rows"] = ingredient_rows
    context["nutrient_rows"] = nutrient_rows

    return render(request, "optimizer_ui/formula_detail.html", context)


@login_required
def ingredient_create(request, formula_id):
    formula = get_object_or_404(
        Formula,
        id=formula_id,
        plant__company__owner=request.user
    )

    if request.method == "POST":
        form = IngredientForm(request.POST)

        if form.is_valid():
            ingredient = form.save(commit=False)
            ingredient.formula = formula
            ingredient.ingredient=ingredient.ingredient_master.name
            ingredient.save()
            return redirect("optimizer_ui:formula_detail", formula_id=formula.id)
    else:
        form = IngredientForm()

    return render(request, "optimizer_ui/ingredient_form.html", {
        "form": form,
        "formula": formula,
        "title": "Add Ingredient",
    })


@login_required
def ingredient_update(request, ingredient_id):
    ingredient = get_object_or_404(
        Ingredient,
        id=ingredient_id,
        formula__plant__company__owner=request.user
    )

    if request.method == "POST":
        form = IngredientForm(request.POST, instance=ingredient)

        if form.is_valid():
            ingredient=form.save(commit=False)
            ingredient.ingredient=ingredient.ingredient_master.name
            ingredient.save()
            
            return redirect("optimizer_ui:formula_detail",formula_id=ingredient.formula.id)
    else:
        form = IngredientForm(instance=ingredient)

    return render(request, "optimizer_ui/ingredient_form.html", {
        "form": form,
        "formula": ingredient.formula,
        "title": "Edit Ingredient",
    })


@login_required
def ingredient_delete(request, ingredient_id):
    ingredient = get_object_or_404(
        Ingredient,
        id=ingredient_id,
        formula__plant__company__owner=request.user
    )

    formula_id = ingredient.formula.id

    if request.method == "POST":
        ingredient.delete()
        return redirect("optimizer_ui:formula_detail", formula_id=formula_id)

    return render(request, "optimizer_ui/ingredient_confirm_delete.html", {
        "ingredient": ingredient
    })


@login_required
def formula_create(request, plant_id):
    plant = get_object_or_404(
        Plant,
        id=plant_id,
        company__owner=request.user
    )

    if request.method == "POST":
        form = FormulaForm(request.POST)

        if form.is_valid():
            formula = form.save(commit=False)
            formula.plant = plant
            formula.save()

            return redirect("optimizer_ui:formula_list", plant_id=plant.id)
    else:
        form = FormulaForm()

    return render(request, "optimizer_ui/formula_form.html", {
        "form": form,
        "plant": plant,
        "title": "Add Formula",
    })


@login_required
def formula_update(request, formula_id):
    formula = get_object_or_404(
        Formula,
        id=formula_id,
        plant__company__owner=request.user
    )

    if request.method == "POST":
        form = FormulaForm(request.POST, instance=formula)

        if form.is_valid():
            form.save()
            return redirect(
                "optimizer_ui:formula_list",
                plant_id=formula.plant.id
            )
    else:
        form = FormulaForm(instance=formula)

    return render(request, "optimizer_ui/formula_form.html", {
        "form": form,
        "plant": formula.plant,
        "title": "Edit Formula",
    })


@login_required
def formula_delete(request, formula_id):
    formula = get_object_or_404(
        Formula,
        id=formula_id,
        plant__company__owner=request.user
    )

    plant_id = formula.plant.id

    if request.method == "POST":
        formula.delete()
        return redirect("optimizer_ui:formula_list", plant_id=plant_id)

    return render(request, "optimizer_ui/formula_confirm_delete.html", {
        "formula": formula
    })


@login_required
def nutrient_constraint_create(request, formula_id):
    formula = get_object_or_404(
        Formula,
        id=formula_id,
        plant__company__owner=request.user
    )

    if request.method == "POST":
        form = NutrientConstraintForm(request.POST)

        if form.is_valid():
            constraint = form.save(commit=False)
            constraint.formula = formula
            constraint.save()

            return redirect("optimizer_ui:formula_detail", formula_id=formula.id)
    else:
        form = NutrientConstraintForm()

    return render(request, "optimizer_ui/nutrient_constraint_form.html", {
        "form": form,
        "formula": formula,
        "title": "Add Nutrient Requirement",
    })


@login_required
def nutrient_constraint_delete(request, constraint_id):
    constraint = get_object_or_404(
        NutrientConstraint,
        id=constraint_id,
        formula__plant__company__owner=request.user
    )

    formula_id = constraint.formula.id

    if request.method == "POST":
        constraint.delete()
        return redirect("optimizer_ui:formula_detail", formula_id=formula_id)

    return render(request, "optimizer_ui/nutrient_constraint_confirm_delete.html", {
        "constraint": constraint
    })

@login_required
def maintenance_home(request):
    return render(request, "optimizer_ui/maintenance_home.html")


@login_required
def nutrient_list(request):
    nutrients = Nutrient.objects.all().order_by("name")

    return render(request, "optimizer_ui/nutrient_list.html", {
        "nutrients": nutrients,
    })


@login_required
def nutrient_create(request):
    if request.method == "POST":
        form = NutrientForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("optimizer_ui:nutrient_list")
    else:
        form = NutrientForm()

    return render(request, "optimizer_ui/nutrient_form.html", {
        "form": form,
        "title": "Add Nutrient",
    })


@login_required
def nutrient_update(request, nutrient_id):
    nutrient = get_object_or_404(Nutrient, id=nutrient_id)

    if request.method == "POST":
        form = NutrientForm(request.POST, instance=nutrient)

        if form.is_valid():
            form.save()
            return redirect("optimizer_ui:nutrient_list")
    else:
        form = NutrientForm(instance=nutrient)

    return render(request, "optimizer_ui/nutrient_form.html", {
        "form": form,
        "title": "Edit Nutrient",
    })


@login_required
def nutrient_delete(request, nutrient_id):
    nutrient = get_object_or_404(Nutrient, id=nutrient_id)

    if request.method == "POST":
        nutrient.delete()
        return redirect("optimizer_ui:nutrient_list")

    return render(request, "optimizer_ui/nutrient_confirm_delete.html", {
        "nutrient": nutrient,
    })
@login_required
def ingredient_nutrient_list(request, ingredient_id):
    ingredient = get_object_or_404(
        Ingredient,
        id=ingredient_id,
        formula__plant__company__owner=request.user
    )

    nutrient_values = (
        IngredientNutrient.objects
        .select_related("nutrient")
        .filter(ingredient=ingredient)
        .order_by("nutrient__name")
    )

    return render(request, "optimizer_ui/ingredient_nutrient_list.html", {
        "ingredient": ingredient,
        "formula": ingredient.formula,
        "nutrient_values": nutrient_values,
    })


@login_required
def ingredient_nutrient_create(request, ingredient_id):
    ingredient = get_object_or_404(
        Ingredient,
        id=ingredient_id,
        formula__plant__company__owner=request.user
    )

    if request.method == "POST":
        form = IngredientNutrientForm(request.POST)

        if form.is_valid():
            value = form.save(commit=False)
            value.ingredient = ingredient
            value.save()

            return redirect(
                "optimizer_ui:ingredient_nutrient_list",
                ingredient_id=ingredient.id
            )
    else:
        form = IngredientNutrientForm()

    return render(request, "optimizer_ui/ingredient_nutrient_form.html", {
        "form": form,
        "ingredient": ingredient,
        "title": "Add Nutrient Value",
    })


@login_required
def ingredient_nutrient_update(request, value_id):
    value = get_object_or_404(
        IngredientNutrient,
        id=value_id,
        ingredient__formula__plant__company__owner=request.user
    )

    if request.method == "POST":
        form = IngredientNutrientForm(request.POST, instance=value)

        if form.is_valid():
            form.save()
            return redirect(
                "optimizer_ui:ingredient_nutrient_list",
                ingredient_id=value.ingredient.id
            )
    else:
        form = IngredientNutrientForm(instance=value)

    return render(request, "optimizer_ui/ingredient_nutrient_form.html", {
        "form": form,
        "ingredient": value.ingredient,
        "title": "Edit Nutrient Value",
    })


@login_required
def ingredient_nutrient_delete(request, value_id):
    value = get_object_or_404(
        IngredientNutrient,
        id=value_id,
        ingredient__formula__plant__company__owner=request.user
    )

    ingredient_id = value.ingredient.id

    if request.method == "POST":
        value.delete()
        return redirect(
            "optimizer_ui:ingredient_nutrient_list",
            ingredient_id=ingredient_id
        )

    return render(request, "optimizer_ui/ingredient_nutrient_confirm_delete.html", {
        "value": value,
        "ingredient": value.ingredient,
    })
@login_required
def ingredient_master_list(request):
    ingredients = IngredientMaster.objects.all().order_by("name")

    return render(request, "optimizer_ui/ingredient_master_list.html", {
        "ingredients": ingredients,
    })


@login_required
def ingredient_master_create(request):
    if request.method == "POST":
        form = IngredientMasterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("optimizer_ui:ingredient_master_list")
    else:
        form = IngredientMasterForm()

    return render(request, "optimizer_ui/ingredient_master_form.html", {
        "form": form,
        "title": "Add Ingredient",
    })


@login_required
def ingredient_master_update(request, ingredient_id):
    ingredient = get_object_or_404(IngredientMaster, id=ingredient_id)

    if request.method == "POST":
        form = IngredientMasterForm(request.POST, instance=ingredient)

        if form.is_valid():
            form.save()
            return redirect("optimizer_ui:ingredient_master_list")
    else:
        form = IngredientMasterForm(instance=ingredient)

    return render(request, "optimizer_ui/ingredient_master_form.html", {
        "form": form,
        "title": "Edit Ingredient",
    })


@login_required
def ingredient_master_delete(request, ingredient_id):
    ingredient = get_object_or_404(IngredientMaster, id=ingredient_id)

    if request.method == "POST":
        ingredient.delete()
        return redirect("optimizer_ui:ingredient_master_list")

    return render(request, "optimizer_ui/ingredient_master_confirm_delete.html", {
        "ingredient": ingredient,
    })
@login_required
def base_nutrient_list(request, ingredient_id):
    ingredient = get_object_or_404(IngredientMaster, id=ingredient_id)

    values = (
        BaseIngredientNutrient.objects
        .select_related("nutrient")
        .filter(ingredient_master=ingredient)
        .order_by("nutrient__name")
    )

    return render(request, "optimizer_ui/base_nutrient_list.html", {
        "ingredient": ingredient,
        "values": values,
    })


@login_required
def base_nutrient_create(request, ingredient_id):
    ingredient = get_object_or_404(IngredientMaster, id=ingredient_id)

    if request.method == "POST":
        form = BaseIngredientNutrientForm(request.POST)

        if form.is_valid():
            value = form.save(commit=False)
            value.ingredient_master = ingredient
            value.save()
            return redirect("optimizer_ui:base_nutrient_list", ingredient_id=ingredient.id)
    else:
        form = BaseIngredientNutrientForm()

    return render(request, "optimizer_ui/base_nutrient_form.html", {
        "form": form,
        "ingredient": ingredient,
        "title": "Add Base Nutrient Value",
    })


@login_required
def base_nutrient_update(request, value_id):
    value = get_object_or_404(BaseIngredientNutrient, id=value_id)

    if request.method == "POST":
        form = BaseIngredientNutrientForm(request.POST, instance=value)

        if form.is_valid():
            form.save()
            return redirect(
                "optimizer_ui:base_nutrient_list",
                ingredient_id=value.ingredient_master.id
            )
    else:
        form = BaseIngredientNutrientForm(instance=value)

    return render(request, "optimizer_ui/base_nutrient_form.html", {
        "form": form,
        "ingredient": value.ingredient_master,
        "title": "Edit Base Nutrient Value",
    })


@login_required
def base_nutrient_delete(request, value_id):
    value = get_object_or_404(BaseIngredientNutrient, id=value_id)
    ingredient_id = value.ingredient_master.id

    if request.method == "POST":
        value.delete()
        return redirect("optimizer_ui:base_nutrient_list", ingredient_id=ingredient_id)

    return render(request, "optimizer_ui/base_nutrient_confirm_delete.html", {
        "value": value,
        "ingredient": value.ingredient_master,
    })
@login_required
def optimization_run_list(request):
    runs = (
        OptimizationRun.objects
        .select_related("formula", "formula__plant", "formula__plant__company")
        .filter(formula__plant__company__owner=request.user)
        .order_by("-created_at")
    )

    return render(request, "optimizer_ui/optimization_run_list.html", {
        "runs": runs,
    })

@login_required
def optimization_run_detail(request, run_id):
    run = get_object_or_404(
        OptimizationRun.objects.select_related(
            "formula",
            "formula__plant",
            "formula__plant__company"
        ),
        id=run_id,
        formula__plant__company__owner=request.user
    )

    ingredient_snapshots = run.ingredient_snapshots.all().order_by("ingredient_name")
    nutrient_snapshots = run.nutrient_snapshots.all().order_by("nutrient_name")

    return render(request, "optimizer_ui/optimization_run_detail.html", {
        "run": run,
        "ingredient_snapshots": ingredient_snapshots,
        "nutrient_snapshots": nutrient_snapshots,
    })
@login_required
def plant_overlay_list(request, plant_id):
    plant = get_object_or_404(
        Plant,
        id=plant_id,
        company__owner=request.user
    )

    overlays = (
        PlantIngredientNutrientOverlay.objects
        .filter(plant=plant)
        .select_related(
            "ingredient_master",
            "nutrient"
        )
        .order_by(
            "ingredient_master__name",
            "nutrient__name"
        )
    )

    return render(
        request,
        "optimizer_ui/plant_overlay_list.html",
        {
            "plant": plant,
            "overlays": overlays,
        }
    )
@login_required
def plant_overlay_create(request, plant_id):
    plant = get_object_or_404(
        Plant,
        id=plant_id,
        company__owner=request.user
    )

    if request.method == "POST":
        form = PlantIngredientNutrientOverlayForm(request.POST)

        if form.is_valid():
            overlay = form.save(commit=False)
            overlay.plant = plant
            overlay.save()

            return redirect(
                "optimizer_ui:plant_overlay_list",
                plant_id=plant.id
            )
    else:
        form = PlantIngredientNutrientOverlayForm()

    return render(request, "optimizer_ui/plant_overlay_form.html", {
        "form": form,
        "plant": plant,
        "title": "Add Overlay",
    })
@login_required
def plant_overlay_update(request, overlay_id):
    overlay = get_object_or_404(
        PlantIngredientNutrientOverlay,
        id=overlay_id,
        plant__company__owner=request.user
    )

    if request.method == "POST":
        form = PlantIngredientNutrientOverlayForm(request.POST, instance=overlay)

        if form.is_valid():
            form.save()
            return redirect(
                "optimizer_ui:plant_overlay_list",
                plant_id=overlay.plant.id
            )
    else:
        form = PlantIngredientNutrientOverlayForm(instance=overlay)

    return render(request, "optimizer_ui/plant_overlay_form.html", {
        "form": form,
        "plant": overlay.plant,
        "title": "Edit Overlay",
    })


@login_required
def plant_overlay_delete(request, overlay_id):
    overlay = get_object_or_404(
        PlantIngredientNutrientOverlay,
        id=overlay_id,
        plant__company__owner=request.user
    )

    plant_id = overlay.plant.id

    if request.method == "POST":
        overlay.delete()
        return redirect(
            "optimizer_ui:plant_overlay_list",
            plant_id=plant_id
        )

    return render(request, "optimizer_ui/plant_overlay_confirm_delete.html", {
        "overlay": overlay,
        "plant": overlay.plant,
    })
