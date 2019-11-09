"""Handles operations related to the configuration of predict."""
import os
import stat
import binascii
import configparser


def load_config(file_path):
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str

    if os.path.exists(file_path):
        config.read(file_path)
        return config

    return None


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

    # TODO: Change these to config defaults?

    config.add_section("WHITELIST")
    config.set(
        "WHITELIST",
        "; This section of the configuration is for specifying which users are allowed to",
    )
    config.set(
        "WHITELIST",
        "; register. Aside from WHITELIST_ENABLED, each line here should be a username. ",
    )
    config.set("WHITELIST", "; Every username specified will be permitted to create an account.")
    config["WHITELIST"]["WHITELIST_ENABLED"] = "True"

    config.add_section("SECURITY")
    config.set(
        "SECURITY",
        "; This section lets you configure the security features of predict like secret",
    )
    config.set("SECURITY", "; keys and whether or not authentication is required.")

    config["SECURITY"]["SECRET_KEY"] = random_secret_key(24)
    config["SECURITY"]["LOGIN_REQUIRED"] = "False"

    config.add_section("AUTHENTICATION")
    config.set(
        "AUTHENTICATION",
        "; This section lets you configure the regular expressions used by the registration system.",
    )

    config["AUTHENTICATION"]["USERNAME_REGEX"] = "\\w+"
    config["AUTHENTICATION"]["USERNAME_FEEDBACK"] = "Usernames must be at least one alphanumeric character"
    config["AUTHENTICATION"]["PASSWORD_REGEX"] = "\\w{8,}"
    config["AUTHENTICATION"]["PASSWORD_FEEDBACK"] = "Passwords must be at least eight alphanumeric characters"

    return config


def random_secret_key(length):
    """Generate a random secret key with length bytes"""
    return binascii.hexlify(os.urandom(length)).decode("utf-8")
