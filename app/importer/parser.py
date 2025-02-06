from abc import ABC, abstractmethod
from collections import defaultdict

from .mapping import branch_groups, mapping_branches, mapping_employees_n, mapping_units


PARSER_TYPES = {
    "anteil": "AnteilDataParser",
    "bar": "BarDataParser",
    "base": "BaseDataParser",
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
        :param config: dict, configuration for a specific plot
        :return: dict, parsed data
        """
        pass


class AnteilDataParser(DataParser):
    sheet_basis_prefix = "anteil_"

    def parse(self, sheets, config):
        # Extract Anteil data
        data = self.extract(sheets)

        return data

    def extract(self, sheets):
        """
        Extract Anteil data.

        :param sheets: dict, where keys are names of sheets and values are pandas DataFrames
        :return: nested dict, with the following shape {area: {year: {unit: {branch: value}}}}
        """
        extracted = init_nested_dict()

        for sheet_key in sheets:
            if not sheet_key.startswith(self.sheet_basis_prefix):
                continue

            type, year, area = sheet_key[len(self.sheet_basis_prefix) :].split("_")
            df = sheets[sheet_key]

            for branch in mapping_branches:
                # Add the number of employees to those branches which refer to the company size
                df["Wirtschaftsgliederung"] = df.apply(self.apply_mapping, axis=1)

                # Process each non-empty row
                row = df.loc[df["Wirtschaftsgliederung"] == branch]
                if row.empty:
                    continue

                # Else extract value for each certain unit from the row
                mapped_branch = mapping_branches[branch]
                for unit in mapping_units:
                    if unit in row:
                        mapped_unit = mapping_units[unit]
                        value = row.iloc[0][unit]
                        extracted[area][year][mapped_unit][mapped_branch] = value

        return extracted

    def apply_mapping(self, row):
        """
        Helper function.
        Apply conditional mapping to rows aggregating companies by size,
        so the name specifies the number of employees.

        :param row: pandas.DataFrame, a data row
        :return: pandas.DataFrame, a data row after applying the mapping
        """
        if row["Wirtschaftsgliederung"] == "Beschäftigte":
            return mapping_employees_n.get(
                row["Nr. der Klassifikation"], row["Wirtschaftsgliederung"]
            )
        else:
            return row["Wirtschaftsgliederung"]


class BaseDataParser(DataParser):
    sheet_basis_prefix = "basis_"

    def parse(self, sheets, config):
        # Extract basis data
        data = self.extract(sheets)

        # Validate and reshape the extracted data
        for area in data:
            for unit in data[area]:
                data[area][unit] = self.reshape(data[area][unit])

        # Add calculations for Berlin/Germany percentage and return on investment
        self.add_berlin_percentage(data)
        self.add_investment_return(data)

        return data

    def extract(self, sheets):
        """
        Extract Basis data.

        :param sheets: dict, where keys are names of sheets and values are pandas DataFrames
        :return: nested dict, with the following shape {area: {unit: {branch: {year: value}}}}
        """
        extracted = init_nested_dict()

        for sheet_key in sheets:
            if not sheet_key.startswith(self.sheet_basis_prefix):
                continue

            year, area = sheet_key[len(self.sheet_basis_prefix) :].split("_")
            df = sheets[sheet_key]

            for branch in mapping_branches:
                # Add the number of employees to those branches which refer to the company size
                df["Wirtschaftsgliederung"] = df.apply(self.apply_mapping, axis=1)

                # Process each non-empty row
                row = df.loc[df["Wirtschaftsgliederung"] == branch]
                if row.empty:
                    continue

                # Else extract value for each certain unit from the row
                mapped_branch = mapping_branches[branch]
                for unit in mapping_units:
                    if unit in row:
                        mapped_unit = mapping_units[unit]
                        value = row.iloc[0][unit]
                        extracted[area][mapped_unit][mapped_branch][year] = value

        return extracted

    def reshape(self, input_dict):
        """
        Validate and reshape the extracted data.

        :param input_dict: nested dict, with the shape {branch: {year: value}}
        :return: dict, with the shape {years: [year1, year2, ...], branch1: [value1, value2, ...]}
        """
        # Make an ordered list of all years that are present in the dataset
        years = set()
        for branch_values in input_dict.values():
            years.update(year for year in branch_values.keys())

        # Check that all inner dictionaries contain all the years and reshape them
        output_dict = {"x": sorted(list(int(year) for year in years))}
        for branch, branch_values in input_dict.items():
            if set(branch_values.keys()) != years:
                raise Exception  # TODO: Make more specific exception
            output_dict[branch] = [year_value for year_value in branch_values.values()]

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
            return mapping_employees_n.get(
                row["Nr. der Klassifikation"], row["Wirtschaftsgliederung"]
            )
        else:
            return row["Wirtschaftsgliederung"]

    def add_berlin_percentage(self, data):
        """
        Add percentage of Berlin with respect to Germany.
        """
        ber_de_percentages = init_nested_dict()

        for unit in data["ber"]:
            for branch in data["ber"][unit]:
                if branch == "x":
                    ber_de_percentages[unit]["x"] = data["ber"][unit]["x"]
                else:
                    percentages = []
                    for i, value in enumerate(data["ber"][unit][branch]):
                        if (
                            data["ber"][unit][branch][i] == 0
                            or data["de"][unit][branch][i] == 0
                        ):
                            percentage = 0
                        else:
                            percentage = (
                                data["ber"][unit][branch][i]
                                / data["de"][unit][branch][i]
                                * 100
                            )
                        percentages.append(round(percentage, 2))
                    ber_de_percentages[unit][branch] = percentages

        data["ber_de_percentages"] = ber_de_percentages

    def add_investment_return(self, data):
        """
        Add calculations for return on investment.
        """
        for area in data:
            investment_returns = init_nested_dict()

            for denominator in ["umsatz_mio_produkt", "umsatz_mio", "fue_ausgaben"]:
                if denominator in data[area]:
                    investment_returns[denominator] = init_nested_dict()
                    investment_returns[denominator]["x"] = data[area][
                        "innovations_ausgaben_mio"
                    ]["x"]

                    for i, branch in enumerate(data[area]["innovations_ausgaben_mio"]):
                        if branch != "x":
                            investment_returns[denominator][branch] = []
                            for i, value in enumerate(
                                data[area]["innovations_ausgaben_mio"][branch]
                            ):
                                if (
                                    value == 0
                                    or data[area][denominator][branch][i] == 0
                                ):
                                    result = 0
                                else:
                                    result = value / data[area][denominator][branch][i]
                                investment_returns[denominator][branch].append(result)

            data[area]["investment_returns"] = investment_returns


class BarDataParser(DataParser):
    def parse(self, sheets, config):
        data = self.extract(sheets, config)

        return data

    def extract(self, sheets, config):
        """
        Extract bar data.

        :param sheets: dict, where keys are names of sheets and values are pandas DataFrames
        :return: nested dict, with the following shape:
            {area: {year: {criteria: {"x": [branch1, branch2, ...], "y": [value1, value2, ...]}}}}
        """
        extracted = init_nested_dict()
        for sheet_key in sheets:
            sheet_key_regex = config["sheet_key_regex"]
            if sheet_key_regex in sheet_key:
                year, area = sheet_key.removeprefix(sheet_key_regex + "_").split("_")
                df = sheets[sheet_key]

                for _, row in df.iterrows():
                    branch = row["Branche"]
                    if branch_groups.get(branch) == "individual":
                        for criteria in config["filters"]["single_choice_2"]:
                            if criteria not in extracted[area][year]:
                                extracted[area][year][criteria] = {"x": [], "y": []}
                            extracted[area][year][criteria]["x"].append(branch)
                            extracted[area][year][criteria]["y"].append(row[criteria])

        return extracted


class FUEDataParser(DataParser):
    def parse(self, sheets, config):
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


class GrowthDataParser(DataParser):
    def parse(self, sheets, config):
        data = self.extract(sheets)

        return data

    def extract(self, sheets):
        """
        Extract shares data.

        :param sheets: dict, where keys are names of sheets and values are pandas DataFrames
        :return: nested dict, with the following shape:
            {area: {
                group: {
                    "labels": [l1, l2, ...],
                    "x": [x1, x2, ...],
                    "y": [y1, y2, ...],
                    "z": [z1, z2, ...],
            }}}
        """
        extracted = init_nested_dict()
        for sheet_key in sheets:
            if "relevanzbubbles" in sheet_key:
                relevanzbubbles, area = sheet_key.split("_")
                df = sheets[sheet_key]

                for _, row in df.iterrows():
                    branch = row["Wirtschaftsgliederung"]
                    if branch in branch_groups:
                        group = branch_groups[branch]

                        if "labels" not in extracted[area][group]:
                            extracted[area][group]["labels"] = []
                        extracted[area][group]["labels"].append(branch)

                        if "x" not in extracted[area][group]:
                            extracted[area][group]["x"] = []
                        extracted[area][group]["x"].append(row["FuE-Ausgaben 2021"])

                        if "y" not in extracted[area][group]:
                            extracted[area][group]["y"] = []
                        extracted[area][group]["y"].append(
                            row["Wachstum FuE-Ausgaben 2018-2021"]
                        )

                        if "z" not in extracted[area][group]:
                            extracted[area][group]["z"] = []
                        extracted[area][group]["z"].append(
                            row["Umsatz mit Produktneuheiten in Mio. €"]
                        )

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
