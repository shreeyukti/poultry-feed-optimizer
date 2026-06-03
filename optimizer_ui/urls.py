from django.urls import path
from . import views

app_name = "optimizer_ui"

urlpatterns = [
    path("", views.login_view, name="login"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),

    path("home/", views.home, name="home"),

    path("plants/", views.plant_list, name="plant_list"),

    path(
        "plants/<int:plant_id>/formulas/",
        views.formula_list,
        name="formula_list"
    ),

    path(
        "formulas/<int:formula_id>/",
        views.formula_detail,
        name="formula_detail"
    ),
    path(
    "formulas/<int:formula_id>/ingredients/add/",
    views.ingredient_create,
    name="ingredient_create"
),
path(
    "ingredients/<int:ingredient_id>/edit/",
    views.ingredient_update,
    name="ingredient_update"
),
path(
    "ingredients/<int:ingredient_id>/delete/",
    views.ingredient_delete,
    name="ingredient_delete"
),
path(
    "plants/<int:plant_id>/formulas/add/",
    views.formula_create,
    name="formula_create"
),
path(
    "formulas/<int:formula_id>/edit/",
    views.formula_update,
    name="formula_update"
),
path(
    "formulas/<int:formula_id>/delete/",
    views.formula_delete,
    name="formula_delete"
),
path(
    "formulas/<int:formula_id>/requirements/add/",
    views.nutrient_constraint_create,
    name="nutrient_constraint_create"
),
path(
    "requirements/<int:constraint_id>/delete/",
    views.nutrient_constraint_delete,
    name="nutrient_constraint_delete"
),
path("maintenance/", views.maintenance_home, name="maintenance_home"),

path("maintenance/nutrients/", views.nutrient_list, name="nutrient_list"),
path("maintenance/nutrients/add/", views.nutrient_create, name="nutrient_create"),
path("maintenance/nutrients/<int:nutrient_id>/edit/", views.nutrient_update, name="nutrient_update"),
path("maintenance/nutrients/<int:nutrient_id>/delete/", views.nutrient_delete, name="nutrient_delete"),
path(
    "ingredients/<int:ingredient_id>/nutrients/",
    views.ingredient_nutrient_list,
    name="ingredient_nutrient_list",
),
path(
    "ingredients/<int:ingredient_id>/nutrients/add/",
    views.ingredient_nutrient_create,
    name="ingredient_nutrient_create",
),
path(
    "ingredient-nutrients/<int:value_id>/edit/",
    views.ingredient_nutrient_update,
    name="ingredient_nutrient_update",
),
path(
    "ingredient-nutrients/<int:value_id>/delete/",
    views.ingredient_nutrient_delete,
    name="ingredient_nutrient_delete",
),
path("maintenance/ingredients/", views.ingredient_master_list, name="ingredient_master_list"),
path("maintenance/ingredients/add/", views.ingredient_master_create, name="ingredient_master_create"),
path("maintenance/ingredients/<int:ingredient_id>/edit/", views.ingredient_master_update, name="ingredient_master_update"),
path("maintenance/ingredients/<int:ingredient_id>/delete/", views.ingredient_master_delete, name="ingredient_master_delete"),
path(
    "maintenance/ingredients/<int:ingredient_id>/base-nutrients/",
    views.base_nutrient_list,
    name="base_nutrient_list",
),
path(
    "maintenance/ingredients/<int:ingredient_id>/base-nutrients/add/",
    views.base_nutrient_create,
    name="base_nutrient_create",
),
path(
    "maintenance/base-nutrients/<int:value_id>/edit/",
    views.base_nutrient_update,
    name="base_nutrient_update",
),
path(
    "maintenance/base-nutrients/<int:value_id>/delete/",
    views.base_nutrient_delete,
    name="base_nutrient_delete",
),
path(
    "optimization-runs/",
    views.optimization_run_list,
    name="optimization_run_list",
),
path(
    "optimization-runs/<int:run_id>/",
    views.optimization_run_detail,
    name="optimization_run_detail",
),
path(
    "plants/<int:plant_id>/overlays/",
    views.plant_overlay_list,
    name="plant_overlay_list",
),
path(
    "plants/<int:plant_id>/overlays/add/",
    views.plant_overlay_create,
    name="plant_overlay_create",
),
path(
    "plant-overlays/<int:overlay_id>/edit/",
    views.plant_overlay_update,
    name="plant_overlay_update",
),
path(
    "plant-overlays/<int:overlay_id>/delete/",
    views.plant_overlay_delete,
    name="plant_overlay_delete",
),
]