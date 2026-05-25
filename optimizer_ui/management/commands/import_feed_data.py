from pathlib import Path

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.loader import load_csv
from optimizer_ui.models import (
    Ingredient,
    IngredientNutrient,
    Nutrient,
    NutrientConstraint,
)


BASE_INGREDIENT_COLUMNS = {
    "ingredient",
    "cost",
    "minquantity",
    "maxquantity",
    "currentquantity",
}


class Command(BaseCommand):
    help = "Import ingredient composition and nutrient constraints from CSV files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--ingredients",
            default="data/ingredients.csv",
            help="Ingredient CSV path relative to the project root.",
        )
        parser.add_argument(
            "--constraints",
            default="data/sample_constraints.csv",
            help="Constraint CSV path relative to the project root.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        ingredients_path = self._resolve_path(options["ingredients"])
        constraints_path = self._resolve_path(options["constraints"])

        if not ingredients_path.exists():
            raise CommandError(f"Ingredient file not found: {ingredients_path}")
        if not constraints_path.exists():
            raise CommandError(f"Constraint file not found: {constraints_path}")

        ingredients = load_csv(ingredients_path)
        constraints = load_csv(constraints_path)
        self._validate_columns(ingredients, constraints)

        nutrient_columns = [
            column for column in ingredients.columns if column not in BASE_INGREDIENT_COLUMNS
        ]
        nutrients = {
            column: Nutrient.objects.get_or_create(name=column)[0]
            for column in nutrient_columns
        }

        ingredient_count = 0
        nutrient_value_count = 0
        for _, row in ingredients.iterrows():
            ingredient_name = str(row["ingredient"]).strip()
            ingredient, _ = Ingredient.objects.update_or_create(
                ingredient=ingredient_name,
                defaults={
                    "cost": self._value_or_none(row["cost"]),
                    "minquantity": self._value_or_default(row["minquantity"], 0),
                    "maxquantity": self._value_or_none(row["maxquantity"]),
                },
            )
            ingredient_count += 1

            for nutrient_name, nutrient in nutrients.items():
                value = row[nutrient_name]
                if pd.isna(value):
                    IngredientNutrient.objects.filter(
                        ingredient=ingredient,
                        nutrient=nutrient,
                    ).delete()
                    continue
                IngredientNutrient.objects.update_or_create(
                    ingredient=ingredient,
                    nutrient=nutrient,
                    defaults={"value": value},
                )
                nutrient_value_count += 1

        constraint_count = 0
        for _, row in constraints.iterrows():
            nutrient_name = str(row["nutrient"]).strip().lower()
            nutrient, _ = Nutrient.objects.get_or_create(name=nutrient_name)
            constraint, _ = NutrientConstraint.objects.get_or_create(nutrient=nutrient)
            constraint.min = self._value_or_none(row["min"])
            constraint.max = self._value_or_none(row["max"])
            constraint.save(update_fields=["min", "max"])
            constraint_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Imported "
                f"{ingredient_count} ingredients, "
                f"{len(nutrients)} nutrients, "
                f"{nutrient_value_count} nutrient values, and "
                f"{constraint_count} active constraints."
            )
        )

    def _resolve_path(self, path_value):
        path = Path(path_value)
        if not path.is_absolute():
            path = Path(settings.BASE_DIR) / path
        return path

    def _validate_columns(self, ingredients, constraints):
        required_ingredient_columns = {"ingredient", "cost", "minquantity", "maxquantity"}
        missing_ingredients = required_ingredient_columns - set(ingredients.columns)
        if missing_ingredients:
            raise CommandError(
                f"Ingredients CSV is missing columns: {sorted(missing_ingredients)}"
            )

        required_constraint_columns = {"nutrient", "min", "max"}
        missing_constraints = required_constraint_columns - set(constraints.columns)
        if missing_constraints:
            raise CommandError(
                f"Constraints CSV is missing columns: {sorted(missing_constraints)}"
            )

    def _value_or_none(self, value):
        return None if pd.isna(value) else value

    def _value_or_default(self, value, default):
        return default if pd.isna(value) else value
