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
    active_ingredients = ingredients[ingredients["cost"].notna() & (ingredients["cost"] > 0)]

    active_ingredients = active_ingredients.fillna(0)
    
    
    model, quantity = run_optimization(active_ingredients,constraints)

    status=pulp.LpStatus[model.status]
    if (status=="Optimal"):

        print("Total cost:", pulp.value(model.objective))

        for name,var in quantity.items():
            if var.varValue and var.varValue>0:
                print(name,":",var.varValue)
        print(quantity)
    else:
        print("no valid solution found for the given constraints")