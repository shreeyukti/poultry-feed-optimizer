import pulp
import pandas as pd
def generate_report(model,quantity,ingredients):
    rows=[]
    for name,var in quantity.items():
        optimized_qty=var.value()
        if optimized_qty  is None:
            optimized_qty=0
        ingredient_row=ingredients[ingredients["ingredient"]==name].iloc[0]

        cost=ingredient_row["cost"]

        rows.append({"Ingredient":name, "Optimised Quantity":round(optimized_qty,3),"cost per kg":round(cost,3),"Total cost":round(optimized_qty*cost,3)})
    report_df=pd.DataFrame(rows)
    used_dataframe=report_df[report_df["Optimised Quantity"]>0]

    print(used_dataframe.to_string(index=False))
    print("total quantity:",round(report_df["Optimised Quantity"].sum(), 3))
    print("total cost:",round(pulp.value(model.objective),3))
    report_df.to_csv("optiimised_result.csv",index=False)
    return report_df
