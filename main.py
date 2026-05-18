from config import INGREDIENTS_FILE, CONSTRAINTS_FILE
from core.loader import load_csv

ingredients = load_csv(INGREDIENTS_FILE)
constraints = load_csv(CONSTRAINTS_FILE)

print(ingredients.head())
print(constraints.head())