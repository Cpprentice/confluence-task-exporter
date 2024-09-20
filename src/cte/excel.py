from pathlib import Path

import pandas as pd


def serialize_to_excel(df: pd.DataFrame, path: Path | str):
    path = Path(path)

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(path, engine="xlsxwriter")

    # Write the dataframe data to XlsxWriter. Turn off the default header and
    # index and skip one row to allow us to insert a user defined header.
    df.to_excel(writer, sheet_name="TODO", startrow=1, header=False, index=False)

    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet = writer.sheets["TODO"]

    # Get the dimensions of the dataframe.
    (max_row, max_col) = df.shape

    # Create a list of column headers, to use in add_table().
    column_settings = [{"header": column} for column in df.columns]

    # Add the Excel table structure. Pandas will add the data.
    worksheet.add_table(0, 0, max_row, max_col - 1, {"columns": column_settings})

    # Make the columns wider for clarity.
    worksheet.set_column(0, max_col - 1, 12)

    instruction_sheet = workbook.add_worksheet('Instructions')
    instruction_sheet.write(0, 0, 'This file was created automatically from Confluence. Do not edit manually!')
    instruction_sheet.activate()

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()
