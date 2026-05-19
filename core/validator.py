import pandas as pd

def validate_data(ingredients, constraints):

    errors = []
    warnings=[]

    if ingredients.empty:
        errors.append("Ingredients file is empty")

    if constraints.empty:
        errors.append("Constraints file is empty")

    if "COST" not in ingredients.columns:
        errors.append("COST column is missing")

    else:

        missing_costs= ingredients[ingredients["COST"].isna()]

        for index, row in missing_costs.iterrows():

            ingredient_name = row["ingredient"]
            warnings.append(f"{ingredient_name} ignored because cost is missing")

        negative_costs = ingredients[ingredients["COST"].notna() & (ingredients["COST"] < 0)]

        for index, row in negative_costs.iterrows():
            ingredient_name = row["ingredient"]
            errors.append(f"{ingredient_name} has negative COST")
                                          
    return errors,warnings