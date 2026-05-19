from config import INGREDIENTS_FILE, CONSTRAINTS_FILE
from core.loader import load_csv
from core.validator import validate_data

ingredients=load_csv(INGREDIENTS_FILE)
constraints=load_csv(CONSTRAINTS_FILE)
errors=validate_data(ingredients,constraints)
if errors:
    print(errors)
else:
    print("data loaded successfully")
