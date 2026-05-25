from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Ingredient(models.Model):
    ingredient = models.CharField(max_length=100)
    cost = models.FloatField(null=True, blank=True)
    minquantity = models.FloatField(default=0)
    maxquantity = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.ingredient


class Nutrient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class IngredientNutrient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="nutrient_values"
    )
    nutrient = models.ForeignKey(
        Nutrient,
        on_delete=models.CASCADE
    )
    value = models.FloatField()

    class Meta:
        unique_together = ("ingredient", "nutrient")

    def __str__(self):
        return f"{self.ingredient} - {self.nutrient}: {self.value}"


class NutrientConstraint(models.Model):
    nutrient = models.OneToOneField(
        Nutrient,
        on_delete=models.CASCADE
    )
    min = models.FloatField(null=True, blank=True)
    max = models.FloatField(null=True, blank=True)

    def __str__(self):
        return str(self.nutrient)


@receiver(post_save, sender=Nutrient)
def create_nutrient_constraint(sender, instance, created, **kwargs):
    if created:
        NutrientConstraint.objects.create(nutrient=instance)
