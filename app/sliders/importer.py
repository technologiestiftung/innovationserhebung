from abc import ABC, abstractmethod
import os
from collections import defaultdict
import json
from openpyxl import load_workbook
import pandas as pd

from mapping import mapping_branches, mapping_employees_n, mapping_units, mapping_fue


# TODO:
#   1/ Refactor once I add other parsers.
#      Parsers should inherit from abstract class.
#      Importer should remain generic and parse types of data as wished.
#   2/ Move filepaths to another file


excel_file = "data/basisdaten_clean.xlsx"
outfile_path = "data/outfile.json"


class DataImporter:
    def import_data(self, filepath):
        """
        Main method of the class.
        Import the data from an Excel file.

        :param filepath: str, path to the Excel file containing the data to parse
        """
        sheets = self.load_excel(filepath)
        base_data_parser = BasisDataParser()
        fue_data_parser = FUEDataParser()

        output = {
            'base': base_data_parser.parse(sheets),
            'fue-expenses': fue_data_parser.parse(sheets)
            }
        self.save_to_json(output, outfile_path)

    def load_excel(self, filepath):
        """
        Load Excel and convert to pandas DataFrames.

        :param filepath: str, path to the Excel file containing the data to parse
        :return: dict, where keys are names of sheets and values are pandas DataFrames
        """
        workbook = load_workbook(filename=filepath, data_only=True)
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

    def save_to_json(self, parsed_data, outfile_path):
        """
        Save data to JSON file.

        :param parsed_data: dict, parsed data
        :param outfile_path: str, path to the JSON file where to save the data
        """
        # Replaces the old outfile if it exists
        if os.path.exists(outfile_path):
            os.remove(outfile_path)
        with open(outfile_path, "w") as outfile:
            json.dump(parsed_data, outfile)

class BasisDataParser:
    def parse(self, sheets):
        """
        Main method of the class.
        Parse Basis data step by step.

        :param sheets: dict, where keys are names of sheets and values are pandas DataFrames
        :return: dict, with the shape {years: [y1, y2, ...], branch1: [b1, b2, ...]}
        """
        # Extract basis data
        data = self.extract(sheets)

        # Validate and reshape the extracted data
        for area in data:
            for unit in data[area]:
                data[area][unit] = self.reshape(data[area][unit])

        return data

    def extract(self, sheets):
        """
        Extract Basis data.

        :param sheets: dict, where keys are names of sheets and values are pandas DataFrames
        :return: nested dict, with the following shape {area: {unit: {branch: {year: value}}}}
        """
        extracted = self.init_nested_dict()

        for sheet_key in sheets:
            basis, year, area = sheet_key.split("_")
            if basis == "basis":
                df = sheets[sheet_key]

                for branch in mapping_branches:
                    # Add the number of employees to those branches which refer to the company size
                    df["Wirtschaftsgliederung"] = df.apply(self.apply_mapping, axis=1)

                    # Process each row
                    row = df.loc[df["Wirtschaftsgliederung"] == branch]
                    if not row.empty:

                        # Extract value for each certain unit from the row
                        for unit in mapping_units:
                            if unit in row:
                                value = row.iloc[0][unit]
                                extracted[area][mapping_units[unit]][mapping_branches[branch]][year] = value
        return extracted

    def reshape(self, input_dict):
        """
        Validate and reshape the extracted Basis data for a specific area and unit.

        :param input_dict: nested dict, with the shape {branch: {year: value}}
        :return: dict, with the shape {years: [y1, y2, ...], branch1: [b1, b2, ...]}
        """
        # Make an ordered list of all years that are present in the dataset
        years = []
        for branch in input_dict:
            for year in input_dict[branch].keys():
                if year not in years:
                    years.append(year)

        # Check that all inner dictionaries contain all the years and reshape them
        output_dict = {"jahre": years}
        for branch in input_dict:
            branch_datapoints = []
            for year in years:
                if year in input_dict[branch]:
                    branch_datapoints.append(input_dict[branch][year])
                else:
                    raise Exception  # TODO: Make more specific exception
            output_dict[branch] = branch_datapoints

        return output_dict

    def apply_mapping(self, row):
        """
        Helper function.
        Apply conditional mapping to rows aggregating companies by size,
        so the name specifies the number of employees.

        :param row: pandas.DataFrame, a data row
        :return: pandas.DataFrame, a data row after applying the mapping
        """
        if row["Wirtschaftsgliederung"] == "Beschäftigte":
            return mapping_employees_n.get(row["Nr. der Klas-\nsifikation"], row["Wirtschaftsgliederung"])
        else:
            return row["Wirtschaftsgliederung"]

    def init_nested_dict(self):
        """
        Helper function.
        Initialize a default dictionary recursively,
        i.e., a nested dictionary with an arbitrary number of levels
        and where keys are created automatically if missing.

        :return: defaultdict, a nested dictionary
        """
        return defaultdict(self.init_nested_dict)
    

class FUEDataParser:
    def parse(self, sheets):
        data = self.extract(sheets)

        return data
    
    def extract(self, sheets):
        """
        Extract Fue Expenses data.

        :param sheets: dict, where keys are names of sheets and values are pandas DataFrames
        :return: nested dict, with the following shape {area: {year: {x: unit[], y: value[]}}}
        """
        extracted = self.init_nested_dict()
        relevant_years = [2011, 2020]
        for sheet_key in sheets:
            basis, _, area = sheet_key.split("_")
            if basis == "fue":
                df = sheets[sheet_key]
                row = df.loc[df["Jahr"].isin(relevant_years)]

                for year in relevant_years:
                    extracted[area][str(year)] = {"x": [], "y": []}
                    for unit in mapping_fue:
                        value = row.iloc[0][unit]
                        # I used the original key from the spredsheet here, so it get's displayed properly in the Graph.
                        extracted[area][str(year)]["x"].append(unit)
                        extracted[area][str(year)]["y"].append(value)
        return extracted
    
    def init_nested_dict(self):
        """
        Helper function.
        Initialize a default dictionary recursively,
        i.e., a nested dictionary with an arbitrary number of levels
        and where keys are created automatically if missing.

        :return: defaultdict, a nested dictionary
        """
        return defaultdict(self.init_nested_dict)


# TODO: These two lines are for testing purposes. Remove later.
data_importer = DataImporter()
data_importer.import_data(excel_file)
