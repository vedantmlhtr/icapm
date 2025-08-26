import os
import pandas as pd

def count_datapoints_in_file(filepath):
    """Return number of datapoints (rows * columns) in a CSV or Excel file."""
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".csv":
            df = pd.read_csv(filepath)
        elif ext in [".xls", ".xlsx"]:
            df = pd.read_excel(filepath)
        else:
            return 0  # skip non-table files
        return df.shape[0] * df.shape[1]
    except Exception as e:
        print(f"Could not read {filepath}: {e}")
        return 0

def main():
    raw_dir = "data/raw"
    total_datapoints = 0

    print("Counting datapoints in /data/raw...\n")
    for filename in os.listdir(raw_dir):
        filepath = os.path.join(raw_dir, filename)
        if os.path.isfile(filepath):
            datapoints = count_datapoints_in_file(filepath)
            total_datapoints += datapoints
            print(f"{filename:<30} -> {datapoints:,} datapoints")

    print("\n" + "="*50)
    print(f"TOTAL DATAPOINTS ACROSS ALL FILES: {total_datapoints:,}")
    print("="*50)

if __name__ == "__main__":
    main()