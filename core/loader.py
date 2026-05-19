import pandas as pd

def load_csv(path):
    df=pd.read_csv(path)
    df.columns=df.columns.str.strip()
    
    if "COST" in df.columns:
        df["COST"]=pd.to_numeric(df["COST"],errors="coerce")
    
    return df
