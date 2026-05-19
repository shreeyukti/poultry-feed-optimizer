import pandas as pd

def load_csv(path):

    df = pd.read_csv(path)

    df.columns = df.columns.str.strip().str.lower()

    if "nutrient" in df.columns:
        df["nutrient"] = df["nutrient"].str.strip().str.lower()

    for column in df.columns:
        if column not in ["ingredient", "nutrient"]:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df