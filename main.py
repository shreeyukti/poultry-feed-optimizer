from config import INGREDIENTS_FILE, CONSTRAINTS_FILE
from core.loader import load_csv
from core.validator import validate_data
from core.optimizer import run_optimization
import pulp
ingredients = load_csv(INGREDIENTS_FILE)
constraints = load_csv(CONSTRAINTS_FILE)

errors,warnings = validate_data(ingredients, constraints)

if warnings:
    print("warnings:")
    for warning in warnings:
        print("-",warning)
if errors:
    print("Validation Errors:")
    for error in errors:
        print("-", error)

else:
    print("Data loaded successfully")
    active_ingredients=ingredients.dropna(subset="COST")

    model, quantity = run_optimization(active_ingredients)

    print("Status:",pulp.LpStatus[model.status])
    print("Total cost:", pulp.value(model.objective))

    for name,var in quantity.items():
        if var.varValue and var.varValue>0:
            print(name,var.varValue)
    print(quantity)