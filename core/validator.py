def validate_data(ingredients,constraints):
    errors=[]
    if (ingredients.empty):
        errors.append("ingredients file is empty")
    if (constraints.empty):
        errors.append("nutrient constraints file is empty")
    return errors

