from django.test import TestCase

from .models import Ingredient, IngredientNutrient, Nutrient, NutrientConstraint
from .services.dataframe_loader import load_optimization_dataframes


class OptimizationDatabaseFlowTests(TestCase):
    def setUp(self):
        self.cp = Nutrient.objects.create(name="CP")
        constraint = NutrientConstraint.objects.get(nutrient=self.cp)
        constraint.min = 10
        constraint.max = 12
        constraint.save()

        maize = Ingredient.objects.create(ingredient="Maize", cost=37)
        IngredientNutrient.objects.create(
            ingredient=maize,
            nutrient=self.cp,
            value=10,
        )

    def test_new_nutrient_automatically_has_constraint(self):
        self.assertTrue(NutrientConstraint.objects.filter(nutrient=self.cp).exists())

    def test_database_loader_builds_optimizer_dataframes(self):
        ingredients, constraints = load_optimization_dataframes()

        self.assertEqual(ingredients.loc[0, "ingredient"], "Maize")
        self.assertEqual(ingredients.loc[0, "cp"], 10)
        self.assertEqual(constraints.loc[0, "nutrient"], "cp")
        self.assertEqual(constraints.loc[0, "min"], 10)

    def test_home_view_optimizes_database_values(self):
        response = self.client.post("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["status"], "Optimal")
        self.assertContains(response, "Maize")
        self.assertContains(response, "1000.0")
