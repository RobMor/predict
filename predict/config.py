"""Handles operations related to the configuration of predict."""
import os
import stat
import binascii
import configparser

import predict.auth


WHITELIST_INFO = [
    "This section of the configuration is for specifying which users are allowed to",
    "register. Aside from WHITELIST_ENABLED, each line here should be a username which conformes to the",
    "regex standard specified in SECURITY_INFO. Every username specified will be permitted to create an account.",
]

SECURITY_INFO = [
    "This section lets you configure the security features of predict like secret",
    "keys and whether or not authentication is required.",
]

AUTH_INFO = "This section lets you configure the regular expressions used by the registration system."
DB_INFO = "This section lets you configure location of the database used by predict."


def config_location():
    return os.environ.get("PREDICT_CONFIG") or os.path.expanduser(
        os.path.join("~", ".predict", "config.ini")
    )


def load_config(file_path):
    """
        If a config already exists at a given location, load it and return its configuration object
    """
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str

    if os.path.exists(file_path):
        try:
            config.read(file_path)
            validate_config(config, file_path)
        except configparser.Error as e:
            # If there is a malformed config, print a general error message, and do not let the application continue.
            import sys

            print("Predict Configuration Error: {}".format(e))
            sys.exit(1)
        return config

    return None  # Otherwise return None, because there is no config at given location


def validate_config(config, file_path):
    # TODO make sure all required fields are there.
    # TODO make sure that all fields that should be booleans are booleans...
    # TODO make sure regular expressions are valid by trying to compile them

    # TODO only run this check when whitelist is enabled
    for username in config["WHITELIST"]:
        if username != "WHITELIST_ENABLED":
            if not predict.auth.string_match(
                username, config["AUTHENTICATION"]["USERNAME_REGEX"]
            ):
                raise configparser.Error(
                    "The username '{}' does not conform to the regex '{}'".format(
                        username, config["AUTHENTICATION"]["USERNAME_REGEX"]
                    )
                )


def write_config(config, file_path):
    """
        Writes the config file and creates a new configs directory if one
        does not exist, and return True if path refers to an existing path. Returns True for broken symbolic links. Equivalent to exists() on platforms lacking os.lstat().y.
    """
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    with open(file_path, "w") as f:
        config.write(f)

    # Set file permissions to only this user
    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)


def create_default_config():
    """Creates a default configuraion.

    Fills the configuration file with default regex and an empty whitelist and
    comments describing the sections of the config.ini.

    Args:
        arguments: the arguments (presumably passed in from cli.py) from the command line.
    """
    # By default the configuration file is an empty whitelist with basic username and password requirements.
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str

    config.add_section("WHITELIST")
    config.set("WHITELIST", "; " + WHITELIST_INFO[0])
    config.set("WHITELIST", "; " + WHITELIST_INFO[1])
    config.set("WHITELIST", "; " + WHITELIST_INFO[2])

    config["WHITELIST"]["WHITELIST_ENABLED"] = "True"

    config.add_section("SECURITY")
    config.set("SECURITY", "; " + SECURITY_INFO[0])
    config.set("SECURITY", "; " + SECURITY_INFO[1])

    config["SECURITY"]["SECRET_KEY"] = random_secret_key(24)
    config["SECURITY"]["LOGIN_REQUIRED"] = "False"

    config.add_section("AUTHENTICATION")
    config.set("AUTHENTICATION", "; " + AUTH_INFO)

    config["AUTHENTICATION"]["USERNAME_REGEX"] = "\\w+"
    config["AUTHENTICATION"][
        "USERNAME_FEEDBACK"
    ] = "Usernames must be at least one alphanumeric character"
    config["AUTHENTICATION"]["PASSWORD_REGEX"] = "\\w{8,}"
    config["AUTHENTICATION"][
        "PASSWORD_FEEDBACK"
    ] = "Passwords must be at least eight alphanumeric characters"

    config.add_section("DATABASE")
    config.set("DATABASE", "; " + DB_INFO)

    config["DATABASE"]["LOCATION"] = os.path.expanduser(
        os.path.join("~", ".predict", "db.sqlite")
    )

    return config


def random_secret_key(length):
    """Generate a random secret key with length bytes"""
    return binascii.hexlify(os.urandom(length)).decode("utf-8")
