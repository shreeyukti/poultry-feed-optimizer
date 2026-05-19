import pulp

def run_optimization(ingredients,constraints):

    model=pulp.LpProblem("feed_optimization", pulp.LpMinimize)
    quantity={}
    for index,row in ingredients.iterrows():
        name=row["ingredient"]
        min_qty=row["minquantity"]
        max_qty=row["maxquantity"]
        if min_qty!=min_qty:
            min_qty=0
        if max_qty!=max_qty or max_qty==0:
            max_qty=None
        quantity[name]=pulp.LpVariable(name,lowBound=min_qty, upBound=max_qty)
    total_cost=0
    for index,row in ingredients.iterrows():
        name=row["ingredient"]
        total_cost=total_cost+quantity[name]*row["cost"]
    model+=total_cost
    model+=pulp.lpSum(quantity.values())==1000

    for index,row in constraints.iterrows():
        nutrient=row["nutrient"]
        min_value=row["min"]
        max_value=row["max"]

        if nutrient not in ingredients.columns:
            continue

        nutrient_total=pulp.lpSum(quantity[ingredient_row["ingredient"]]*ingredient_row[nutrient] for i, ingredient_row in ingredients.iterrows())
        if min_value==min_value:
            model += nutrient_total >= (min_value  * 1000)
        if max_value==max_value:
            model += nutrient_total <= (max_value  * 1000)
    model.solve(pulp.PULP_CBC_CMD(msg=False))

    return model,quantity