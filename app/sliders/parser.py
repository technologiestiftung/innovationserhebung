from abc import ABC, abstractmethod
from collections import defaultdict

from mapping import mapping_branches, mapping_employees_n, mapping_units


PARSER_TYPES = {
    "base": "BasisDataParser",
    "fue": "FUEDataParser",
    "growth": "GrowthDataParser",
    "shares": "SharesDataParser",
}


def init_nested_dict():
    """
    Helper function.
    Initialize a default dictionary recursively,
    i.e., a nested dictionary with an arbitrary number of levels
    and where keys are created automatically if missing.

    :return: defaultdict, a nested dictionary
    """
    return defaultdict(init_nested_dict)


class DataParserFactory:
    @staticmethod
    def create_parser(parser_type):
        """
        Create a plotter for a specific plot type.

        :param parser_type: str, parser type
        :return: a parser instance of the specified type
        """
        parser_name = PARSER_TYPES[parser_type]
        cls = globals()[parser_name]

        return cls()


class DataParser(ABC):
    @abstractmethod
    def parse(self, sheets, config):
        """

        :param sheets: dict, where keys are names of sheets and values are pandas DataFrames
        :param config: dict, configuration
        :return: dict, parsed data
        """
        pass


class BasisDataParser(DataParser):
    def parse(self, sheets, config):
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
        extracted = init_nested_dict()

        for sheet_key in sheets:
            if "basis" in sheet_key:
                basis, year, area = sheet_key.split("_")
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
        :return: dict, with the shape {years: [year1, year2, ...], branch1: [value1, value2, ...]}
        """
        # Make an ordered list of all years that are present in the dataset
        years = []
        for branch in input_dict:
            for year in input_dict[branch].keys():
                if year not in years:
                    years.append(year)

        # Check that all inner dictionaries contain all the years and reshape them
        output_dict = {"jahre": [int(year) for year in years]}
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


class FUEDataParser(DataParser):
    def parse(self, sheets, config):
        config = config["fue_pie_interactive"]
        data = self.extract(sheets, config)

        return data

    def extract(self, sheets, config):
        """
        Extract FUE Expenses data.

        :param sheets: dict, where keys are names of sheets and values are pandas DataFrames
        :return: nested dict, with the following shape:
            {area: {year: {"x": [branch1, branch2, ...], "y": [value1, value2, ...]}}}
        """
        extracted = init_nested_dict()
        relevant_years = config["filters"]["single_choice"]
        branches = config["filters"]["single_choice_highlight"]

        for sheet_key in sheets:
            if "fue_ausgaben" in sheet_key:
                fue, ausgaben, area = sheet_key.split("_")
                df = sheets[sheet_key]

                for year in relevant_years:
                    extracted[area][year] = {"x": [], "y": []}
                    for branch in branches:
                        row = df.loc[df["Jahr"] == int(year)]
                        value = row.iloc[0][branch]
                        extracted[area][year]["x"].append(branch)
                        extracted[area][year]["y"].append(value)
        return extracted


class SharesDataParser(DataParser):
    def parse(self, sheets, config):
        data = self.extract(sheets)

        return data

    def extract(self, sheets):
        """
        Extract shares data.

        :param sheets: dict, where keys are names of sheets and values are pandas DataFrames
        :return: nested dict, with the following shape:
            {area: {year: {"x": [branch1, branch2, ...], "y": [value1, value2, ...]}}}
        """
        extracted = init_nested_dict()
        for sheet_key in sheets:
            if "anteile" in sheet_key:
                anteile, branchen, area = sheet_key.split("_")
                df = sheets[sheet_key]

                years = list(df)[1:]
                for year in years:
                    extracted[area][str(year)] = {"x": [], "y": []}
                    for _, row in df.iterrows():
                        extracted[area][str(year)]["x"].append(row["Branche"])
                        extracted[area][str(year)]["y"].append(round(row[year], 1))

        return extracted


class GrowthDataParser:
    def parse(self, sheets, config):
        return {}
