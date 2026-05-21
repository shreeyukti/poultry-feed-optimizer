import pandas as pd

def validate_data(ingredients, constraints):
    errors = []
    warnings=[]

    if ingredients.empty:
        errors.append("Ingredients file is empty")

    if constraints.empty:
        errors.append("Constraints file is empty")

    if "cost" not in ingredients.columns:
        errors.append("cost column is missing")

    else:
        missing_costs= ingredients[ingredients["cost"].isna()]
        for index, row in missing_costs.iterrows():
            ingredient_name = row["ingredient"]
            warnings.append(f"{ingredient_name} ignored because cost is missing")
        negative_costs = ingredients[ingredients["cost"].notna() & (ingredients["cost"] < 0)]

        for index, row in negative_costs.iterrows():
            ingredient_name = row["ingredient"]
            errors.append(f"{ingredient_name} has negative ")
                                          
    return errors,warnings