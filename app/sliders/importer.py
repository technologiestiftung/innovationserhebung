from abc import ABC, abstractmethod
from collections import defaultdict
import json
from openpyxl import load_workbook
import pandas as pd


# TODO:
#   1/ Refactor in classes, probably using Strategy or Template Method
#   2/ Separate code in appropriate modules
#   3/ Handle entries by size of companies (branches) inside import_excel()
#   4/ Document properly


excel_file = "basisdaten_clean.xlsx"

mapping_branches = {
    "Nahrung/Getränke/Tabak": "nahrung",
    "Pharma/Chemie/Kunststoff": "pharma",
    "Textil/Chemie/Kunststoff": "pharma",
    "Holz/Papier/Druck": "holz",
    "Metall/Glas/Steinwaren": "metall",
    "Elektroindustrie/Instrumententechnik": "elektroindustrie",
    "Maschinen-/Fahrzeugbau": "fahrzeugbau",
    "sonstige Konsumgüter": "sonstige_konsumgüter",
    "Energie/Wasser/Entsorgung": "energie",
    "Verlage/Film/Rundfunk/Telekommunikation": "telekommunikation",
    "Software/Datenverarbeitung": "software",
    "Finanzdienstleistungen": "finanz",
    "Unternehmensberatung": "unternehmensberatung",
    "Architektur-/Ingenieurbüros/techn. Labore": "architektur",
    "Forschung und Entwicklung": "forschung",
    "Kreativdienstleistungen": "kreativ",
    "Industrie": "industrie",
    "Dienstleistungen": "dienstleistungen",
    "Insgesamt": "insgesamt",
    "Beschäftigte_5_9": "beschaeftigte_5_9",
    "Beschäftigte_10_19": "beschaeftigte_10_19",
    "Beschäftigte_20_49": "beschaeftigte_20_49",
    "Beschäftigte_50_249": "beschaeftigte_50_249",
    "Beschäftigte_250_999": "beschaeftigte_250_999",
    "Beschäftigte_1000": "beschaeftigte_1000",
}

mapping_units = {
    "Anzahl der Unternehmen insgesamt": "anzahl_unternehmen_insgesamt",
    "Anzahl der innovations-aktiven Unternehmen": "anzahl_innovative_unternehmen",
    "Anzahl der Innovatoren": "anzahl_innovatoren",
    "Anzahl Beschäftigte": "anzahl_beschaeftigte",
    "Umsatz in Mio. €": "umsatz_mio",
    "Umsatz mit Produktneu-heiten in Mio. €": "umsatz_mio_produkt",
    "Umsatz mit Marktneu-heiten in Mio. €": "umsatz_mio_markt",
    "Innovations-ausgaben in Mio. €": "innovations_ausgaben_mio",
    "FuE-Ausgaben in Mio. €": "fue_ausgaben_mio",
}



class Importer(ABC):
    pass



def load_excel(file_path):
    workbook = load_workbook(filename=file_path, data_only=True)
    sheets_data = {}

    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]

        data = sheet.values
        columns = next(data)[0:]
        df = pd.DataFrame(data, columns=columns)

        # Remove rows and columns with empty values
        df = df.dropna(axis="index", how="all")
        df = df.dropna(axis="columns", how="all")

        sheets_data[sheet_name] = df

    return sheets_data


def init_nested_dict():
    """
    Initialize a default dictionary recursively,
    i.e., a nested dictionary with an arbitrary number of levels
    and where keys are created automatically if missing.

    :return: defaultdict, a nested dictionary
    """
    return defaultdict(init_nested_dict)


class DataParser(ABC):
    def parse_data(self, sheets):
        extracted = init_nested_dict()

        # Step 1
        for sheet_key in sheets:
            basis, year, area = sheet_key.split("_")
            df = sheets[sheet_key]

            # Step 2
            # Get row for a specific branch
            for branch in mapping_branches:
                row = df.loc[df["Wirtschaftsgliederung"] == branch]
                if not row.empty:

                    # Extract a certain value from the row
                    for unit in mapping_units:
                        if unit in row:
                            value = row.iloc[0][unit]
                            extracted[area][mapping_branches[branch]][mapping_units[unit]][year] = value

        return extracted


class BasisDataParser(DataParser):
    def dummy_method(self):
        pass


sheets = load_excel(excel_file)
extracted_data = DataParser().parse_data(sheets)

#print(json.dumps(extracted_data, indent=4))
