from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Plant(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="plants")
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class Formula(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name="formulas")
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.plant.name} - {self.name}"


class Ingredient(models.Model):
    formula = models.ForeignKey(Formula, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.CharField(max_length=100)
    cost = models.FloatField(null=True, blank=True)
    minquantity = models.FloatField(default=0)
    maxquantity = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("formula", "ingredient")

    def __str__(self):
        return f"{self.formula.name} - {self.ingredient}"


class Nutrient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=20, default="%")

    def __str__(self):
        return self.name


class IngredientNutrient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="nutrient_values"
    )
    nutrient = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    value = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ingredient", "nutrient"],
                name="unique_ingredient_nutrient"
            )
        ]

    def __str__(self):
        return f"{self.ingredient} - {self.nutrient}: {self.value}"


class NutrientConstraint(models.Model):
    formula = models.ForeignKey(
        Formula,
        on_delete=models.CASCADE,
        related_name="nutrient_constraints"
    )
    nutrient = models.ForeignKey(Nutrient, on_delete=models.CASCADE)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["formula", "nutrient"],
                name="unique_formula_nutrient_constraint"
            )
        ]

    def __str__(self):
        return f"{self.formula.name} - {self.nutrient.name}"


class OptimizationRun(models.Model):
    formula = models.ForeignKey(
        Formula,
        on_delete=models.CASCADE,
        related_name="optimization_runs"
    )
    total_weight = models.FloatField(default=1000)
    total_cost = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.formula.name} - {self.status} - {self.created_at}"


class OptimizationResultItem(models.Model):
    run = models.ForeignKey(
        OptimizationRun,
        on_delete=models.CASCADE,
        related_name="result_items"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()
    cost_contribution = models.FloatField()

    def __str__(self):
        return f"{self.ingredient.ingredient} - {self.quantity} kg"