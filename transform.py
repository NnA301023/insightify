import pandas as pd


if __name__ == "__main__":

    # Load entire file sheet
    superstore_file = "dataset/superstore.xlsx"
    xls = pd.ExcelFile(superstore_file)
    df = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    
    # Mapping dataframe
    data = df["Orders"]
    data_reg_manager = df["People"]
    data_retention = df["Returns"]

    # Set indexing
    mapping_manager = dict(data_reg_manager[["Region", "Regional Manager"]].values)
    list_retentions = data_retention["Order ID"].to_list()

    # Enrich dataset from other sheets
    data["is_retention"] = data["Order ID"].apply(
        lambda order_id: order_id in list_retentions
    )
    data["region_manager"] = data["Region"].apply(
        lambda region: mapping_manager[region]
    )

    # Save into Excel
    data.to_excel("dataset/superstore_enriched.xlsx")