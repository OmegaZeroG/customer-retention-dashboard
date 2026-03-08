import pandas as pd

def load_and_clean_data(path):

    df = pd.read_csv(path, encoding="ISO-8859-1")

    # remove missing customers
    df = df.dropna(subset=["CustomerID"])

    # remove cancelled invoices
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]

    # remove invalid quantities
    df = df[df["Quantity"] > 0]

    # remove invalid prices
    df = df[df["UnitPrice"] > 0]

    # convert date safely
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

    # create revenue column
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

    df = df.dropna(subset=["InvoiceDate"])

    return df