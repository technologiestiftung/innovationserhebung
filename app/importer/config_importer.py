from copy import deepcopy
import os
import yaml


class ConfigImporter:
    def get_config(self):
        """
        Create a config dictionary based on default and custom values.

        :return: dict, configuration
        """
        # Load config files
        config_default = self.load_config_file("../config/default.yaml")
        config_custom = self.load_config_file("../config/custom.yaml")

        config_result = {}
        # Override default values with custom values for each plot
        for plot_name in config_custom:
            plot_config_custom = config_custom[plot_name]
            plot_type = plot_config_custom["plot_type"]
            plot_config_default = config_default[plot_type]

            overwritten_config = self.override_values(
                plot_config_default, plot_config_custom)
            config_result[plot_name] = overwritten_config

        return config_result

    def load_config_file(self, filename):
        """
        Load a config file.

        :param filename: str, name of the YAML config file
        :return: dict, containing config settings
        """
        current_dir = os.path.dirname(__file__)
        config_path = os.path.join(current_dir, filename)

        with open(config_path, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        return config

    def override_values(self, default_config, custom_config):
        """
        Override default values with custom values of a plot configuration.
        Implemented as a recursive function.

        :param default_config: dict, default configuration for a plot type
        :param custom_config: dict, custom configuration for a plot
        """

        overwritten_config = deepcopy(default_config)
        for key, value in custom_config.items():
            if isinstance(value, dict) and key in overwritten_config and isinstance(overwritten_config[key], dict):
                overwritten_config[key] = self.override_values(
                    overwritten_config[key], value)
            else:
                overwritten_config[key] = value
        return overwritten_config
