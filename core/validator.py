import pandas as pd

def validate_data(ingredients, constraints):
    errors = []
    warnings=[]

    if ingredients.empty:
        errors.append("No ingredients have been entered in the database.")

    if constraints.empty:
        errors.append("No nutrient constraints have been entered in the database.")

    if "cost" not in ingredients.columns:
        errors.append("The ingredient cost field is missing.")

    else:
        missing_costs= ingredients[ingredients["cost"].isna()]
        for index, row in missing_costs.iterrows():
            ingredient_name = row["ingredient"]
            warnings.append(f"{ingredient_name} was ignored because its cost is missing.")
        negative_costs = ingredients[ingredients["cost"].notna() & (ingredients["cost"] < 0)]

        for index, row in negative_costs.iterrows():
            ingredient_name = row["ingredient"]
            errors.append(f"{ingredient_name} has a negative cost.")
                                          
    return errors,warnings
