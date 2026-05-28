import pandas as pd

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from optimizer_ui.models import (
    Company,
    Plant,
    Formula,
    Ingredient,
    Nutrient,
    IngredientNutrient,
    NutrientConstraint,
)


class Command(BaseCommand):
    help = "Import feed ingredients and nutrient constraints from CSV files."

    def add_arguments(self, parser):
        parser.add_argument("--ingredients", default="data/ingredients.csv")
        parser.add_argument("--constraints", default="data/constraints.csv")
        parser.add_argument("--company", required=True)
        parser.add_argument("--plant", required=True)
        parser.add_argument("--formula", required=True)
        parser.add_argument("--location", default="")

    def handle(self, *args, **options):
        ingredients_path = options["ingredients"]
        constraints_path = options["constraints"]

        company_name = options["company"]
        plant_name = options["plant"]
        formula_name = options["formula"]
        location = options["location"]

        ingredients_df = pd.read_csv(ingredients_path)
        constraints_df = pd.read_csv(constraints_path)

        ingredients_df.columns = ingredients_df.columns.str.strip().str.lower()
        constraints_df.columns = constraints_df.columns.str.strip().str.lower()

        required_ingredient_columns = {"ingredient", "cost", "minquantity", "maxquantity"}
        missing_ingredient_columns = required_ingredient_columns - set(ingredients_df.columns)

        if missing_ingredient_columns:
            raise CommandError(
                f"Ingredients CSV is missing columns: {sorted(missing_ingredient_columns)}"
            )

        required_constraint_columns = {"nutrient", "min", "max"}
        missing_constraint_columns = required_constraint_columns - set(constraints_df.columns)

        if missing_constraint_columns:
            raise CommandError(
                f"Constraints CSV is missing columns: {sorted(missing_constraint_columns)}"
            )

        nutrient_columns = [
            col for col in ingredients_df.columns
            if col not in ["ingredient", "cost", "minquantity", "maxquantity"]
        ]

        with transaction.atomic():
            company, _ = Company.objects.get_or_create(name=company_name)

            plant, _ = Plant.objects.get_or_create(
                company=company,
                name=plant_name,
                defaults={"location": location},
            )

            formula, _ = Formula.objects.get_or_create(
                plant=plant,
                name=formula_name,
            )

            nutrient_objects = {}

            for nutrient_name in nutrient_columns:
                nutrient, _ = Nutrient.objects.get_or_create(
                    name=nutrient_name.upper(),
                    defaults={"unit": "%"},
                )
                nutrient_objects[nutrient_name] = nutrient

            for _, row in constraints_df.iterrows():
                nutrient_name = str(row["nutrient"]).strip().lower()

                nutrient, _ = Nutrient.objects.get_or_create(
                    name=nutrient_name.upper(),
                    defaults={"unit": "%"},
                )

                NutrientConstraint.objects.update_or_create(
                    formula=formula,
                    nutrient=nutrient,
                    defaults={
                        "min_value": None if pd.isna(row["min"]) else row["min"],
                        "max_value": None if pd.isna(row["max"]) else row["max"],
                    },
                )

            for _, row in ingredients_df.iterrows():
                ingredient_name = str(row["ingredient"]).strip()

                ingredient, _ = Ingredient.objects.update_or_create(
                    formula=formula,
                    ingredient=ingredient_name,
                    defaults={
                        "cost": None if pd.isna(row["cost"]) else row["cost"],
                        "minquantity": 0 if pd.isna(row["minquantity"]) else row["minquantity"],
                        "maxquantity": None if pd.isna(row["maxquantity"]) else row["maxquantity"],
                    },
                )

                for nutrient_column in nutrient_columns:
                    value = row[nutrient_column]

                    if pd.isna(value):
                        continue

                    nutrient = nutrient_objects.get(nutrient_column)

                    if nutrient is None:
                        nutrient, _ = Nutrient.objects.get_or_create(
                            name=nutrient_column.upper(),
                            defaults={"unit": "%"},
                        )

                    IngredientNutrient.objects.update_or_create(
                        ingredient=ingredient,
                        nutrient=nutrient,
                        defaults={"value": value},
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported data for {company_name} → {plant_name} → {formula_name}"
            )
        )