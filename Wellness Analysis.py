"""
RFM Customer Segmentation – Wellness Forever Pharmacy
Author: Archana Saykar

This script performs end-to-end RFM analysis:
- Loads and combines 12 monthly sheets from an Excel file
- Cleans and validates customer mobile numbers
- Cleans transactional data (dates, sales, duplicates)
- Aggregates data to invoice and customer levels
- Computes Recency, Frequency, Monetary metrics
- Builds RFM scores and assigns customer segments
- Exports the final RFM table for reporting / Power BI
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path


# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

# Relative path to the raw Excel file
# Update this if your file name or location is different
DATA_FILE_PATH = Path(r"C:\Users\archa\OneDrive\Desktop\Wellness Data\Data File.xlsx")

# Output path for the final RFM table
OUTPUT_FILE_PATH = Path(r"C:\Users\archa\OneDrive\Desktop\Wellness Data/RFM_output_clean.xlsx")


# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

def load_and_combine_sheets(file_path: Path) -> pd.DataFrame:
    """
    Load all sheets from a multi-sheet Excel file and combine into a single DataFrame.
    Ensures c_mobile is read as string and adds a Month column per sheet.
    """
    xl = pd.ExcelFile(file_path)
    df_list = []

    for sheet in xl.sheet_names:
        # Read each sheet, force c_mobile as string to avoid numeric corruption
        df_sheet = xl.parse(sheet, dtype={"c_mobile": "string"})

        # Extract only digits from the mobile column
        df_sheet["c_mobile"] = df_sheet["c_mobile"].str.extract(r"(\d+)", expand=False)

        # Keep the last 10 digits to handle formats like +91XXXXXXXXXX or leading zeros
        df_sheet["c_mobile"] = df_sheet["c_mobile"].str[-10:]

        # Track the originating sheet/month
        df_sheet["Month"] = sheet

        df_list.append(df_sheet)

    combined = pd.concat(df_list, ignore_index=True)
    return combined


def filter_valid_mobiles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only valid 10-digit Indian mobile numbers.
    Here we restrict to numbers starting with 7, 8, or 9.
    """
    valid_mask = df["c_mobile"].str.fullmatch(r"[7-9]\d{9}")
    df_valid = df[valid_mask].copy()
    return df_valid


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean transaction-level data:
    - Convert invdate to datetime
    - Convert n_net_sales to numeric
    - Drop missing key fields
    - Keep only positive sales
    - Drop exact duplicates on key fields
    """
    # Convert date and amount
    df["invdate"] = pd.to_datetime(df["invdate"], errors="coerce")
    df["n_net_sales"] = pd.to_numeric(df["n_net_sales"], errors="coerce")

    # Remove rows with missing key fields
    df = df.dropna(subset=["invdate", "c_mobile", "n_net_sales"])

    # Keep only positive sales
    df = df[df["n_net_sales"] > 0]

    # Drop duplicates on key fields
    key_cols = ["c_mobile", "invno", "invdate", "itemname", "n_net_sales"]
    df = df.drop_duplicates(subset=key_cols, keep="first")

    return df


def aggregate_to_invoice_level(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate line-level transactions to invoice-level totals per customer and date.
    """
    invoice_df = (
        df.groupby(["c_mobile", "invno", "invdate"], as_index=False)
          .agg(invoice_amount=("n_net_sales", "sum"))
    )
    return invoice_df


def compute_rfm(invoice_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Recency, Frequency, Monetary metrics for each customer based on invoice-level data.
    """
    # Reference date: last invoice date in the dataset
    ref_date = invoice_df["invdate"].max()

    rfm = (
        invoice_df
        .groupby("c_mobile")
        .agg(
            Recency=("invdate", lambda x: (ref_date - x.max()).days),
            Frequency=("invno", "nunique"),
            Monetary=("invoice_amount", "sum")
        )
        .reset_index()
    )

    return rfm


def score_rfm(rfm: pd.DataFrame) -> pd.DataFrame:
    """
    Assign RFM scores (1–5) using quintiles and construct a composite RFM score.
    """
    # R: lower recency is better
    rfm["R_score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)

    # F & M: higher is better
    rfm["F_score"] = pd.qcut(
        rfm["Frequency"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    rfm["M_score"] = pd.qcut(
        rfm["Monetary"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    # Composite RFM score (as a string, e.g. "541")
    rfm["RFM_Score"] = (
        rfm["R_score"].astype(str)
        + rfm["F_score"].astype(str)
        + rfm["M_score"].astype(str)
    )

    return rfm


def assign_segments(rfm: pd.DataFrame) -> pd.DataFrame:
    """
    Map RFM scores to business-friendly customer segments.
    """

    def segment_customer(row):
        r, f, m = row["R_score"], row["F_score"], row["M_score"]

        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif r >= 3 and f >= 3:
            return "Loyal"
        elif r >= 4 and f <= 2:
            return "New Customers"
        elif r <= 2 and f >= 3:
            return "At Risk"
        elif r <= 2 and f <= 2:
            return "Lost"
        else:
            return "Promising"

    rfm["Segment"] = rfm.apply(segment_customer, axis=1)
    return rfm


# -------------------------------------------------------------------
# Main execution pipeline
# -------------------------------------------------------------------

def main():
    # 1. Load and combine data
    if not DATA_FILE_PATH.exists():
        raise FileNotFoundError(f"Data file not found at: {DATA_FILE_PATH}")

    print("Loading and combining sheets...")
    data = load_and_combine_sheets(DATA_FILE_PATH)
    print(f"Combined data shape (raw): {data.shape}")

    # 2. Filter valid mobile numbers
    print("Filtering valid mobile numbers...")
    data = filter_valid_mobiles(data)
    print(f"Data shape after mobile validation: {data.shape}")

    # 3. Clean transactions
    print("Cleaning transaction data...")
    data = clean_transactions(data)
    print(f"Data shape after cleaning: {data.shape}")

    # 4. Aggregate to invoice level
    print("Aggregating to invoice level...")
    invoice_df = aggregate_to_invoice_level(data)
    print(f"Invoice-level data shape: {invoice_df.shape}")

    # 5. Compute RFM metrics
    print("Computing RFM metrics...")
    rfm = compute_rfm(invoice_df)
    print(f"RFM base table shape: {rfm.shape}")

    # 6. Score RFM
    print("Scoring RFM...")
    rfm = score_rfm(rfm)

    # 7. Assign segments
    print("Assigning customer segments...")
    rfm = assign_segments(rfm)

    # 8. Export results
    OUTPUT_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    rfm.to_excel(OUTPUT_FILE_PATH, index=False)
    print(f"RFM table saved to: {OUTPUT_FILE_PATH}")

    # 9. Print segment distribution summary
    print("\nCustomer count by segment:")
    print(rfm["Segment"].value_counts())


if __name__ == "__main__":
    main()
