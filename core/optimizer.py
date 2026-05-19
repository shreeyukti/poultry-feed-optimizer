import pulp

def run_optimization(ingredients):
    model=pulp.LpProblem("feed_optimization", pulp.LpMinimize)
    quantity={}
    for index,row in ingredients.iterrows():
        name=row["ingredient"]
        quantity[name]=pulp.LpVariable(name,lowBound=0)
    total_cost=0
    for index,row in ingredients.iterrows():
        name=row["ingredient"]
        total_cost=total_cost+quantity[name]*row["COST"]
    model+=total_cost
    model+=pulp.lpSum(quantity.values())==1000
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    
    return model,quantity