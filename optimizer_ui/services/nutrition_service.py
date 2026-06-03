from optimizer_ui.models import (
    BaseIngredientNutrient,
    PlantIngredientNutrientOverlay,
)


class NutritionService:

    @staticmethod
    def get_effective_value(
        plant,
        ingredient_master,
        nutrient,
    ):

        overlay = (
            PlantIngredientNutrientOverlay.objects
            .filter(
                plant=plant,
                ingredient_master=ingredient_master,
                nutrient=nutrient,
            )
            .first()
        )

        if overlay:
            return overlay.value

        base = (
            BaseIngredientNutrient.objects
            .filter(
                ingredient_master=ingredient_master,
                nutrient=nutrient,
            )
            .first()
        )

        if base:
            return base.value

        return 0