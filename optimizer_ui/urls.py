from django.urls import path
from . import views


app_name="optimizer_ui"

urlpatterns=[path("", views.plant_list,name="plant_list"),
             path("home/",views.home,name="home"),
             path("plants/",views.plant_list,name="plant_list"),
             path("plants/<int:plant_id>/formulas/", views.formula_list, name="formula_list"),
             path("formulas/<int:formula_id>/",views.formula_detail,name="formula_detail"),]
