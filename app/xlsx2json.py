from .importer.data_importer import DataImporter

"""
In case we have new data through the XLSX file, we can convert it to JSON via
python -m app.xlsx2json
"""
excel_file = "app/data/basisdaten_clean.xlsx"
outfile_path = "app/data/outfile.json"


data_importer = DataImporter()
data_importer.import_data(excel_file, outfile_path)
