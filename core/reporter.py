import pulp
def generate_report(model,quantity,ingredients):
    previous_cost=(ingredients["currentquantity"]*ingredients["cost"]).sum()
    optimized_cost=pulp.value(model.objective)
    difference=previous_cost-optimized_cost
    #print("\n COST SUMMARY:\n")
    #print(ingredients[["ingredient", "currentquantity", "cost"]])
    #print("Previous cost: ",round(previous_cost,3))
    #print("Current cost: ",round(optimized_cost,4))
    #print("Difference: ",round(difference,4))

    for name, var in quantity.items():
        if var.varValue is not None and var.varValue > 0:
            print("nutrient:", name," quantity: ", round(var.varValue, 2))
    print("Total cost:",round(optimized_cost,3))
