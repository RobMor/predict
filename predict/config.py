"""Handles operations related to the configuration of predict."""
import os
import re
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
USERNAME_FEEDBACK = "Usernames must be at least one character"
PASSWORD_FEEDBACK = "Passwords must be at least eight characters"

CONFIG_TEMPLATE = {
    "WHITELIST": {"WHITELIST_ENABLED": "False"},
    "SECURITY": {"SECRET_KEY": binascii.hexlify(os.urandom(24)).decode("utf-8"), "LOGIN_REQUIRED" : "False"},
    "AUTHENTICATION": {"USERNAME_REGEX": ".+", "USERNAME_FEEDBACK": USERNAME_FEEDBACK, "PASSWORD_REGEX": ".{8,}", "PASSWORD_FEEDBACK": PASSWORD_FEEDBACK},
    "DATABASE": {"LOCATION": "" + os.path.expanduser(os.path.join("~", ".predict", "db.sqlite"))},
}

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
            validate_config(config)
        except (configparser.Error, re.error) as e:
            # If there is a malformed config, print a general error message, and do not let the application continue.
            import sys
            print("Configuration file is located at: " + file_path)
            print("Predict Configuration Error: {}".format(e))
            sys.exit(1)
        return config

    return None  # Otherwise return None, because there is no config at given location

def validate_config(config):
    """
        Validates a given configuration file, by ensuring the required options and
        sections are present, the given regexes compile, boolean options have boolean values,
        and the whitelist if enabled conforms to the config specified regex. 

        Args:
            config: the configuration object to validate

        Raises:
            re.error If anything in the given configuration is invalid by Predict's standards
    """

    validate_required_options(config)
    validate_regex(config)
    validate_booleans(config)
    if config.getboolean("WHITELIST", "WHITELIST_ENABLED"):
        validate_whitelist(config)
    
def validate_regex(config):
    """
        Compiles the config's regex patterns to check they are valid.

        Args:
            the configuration object whose regex to validate
    """
    re.compile(config["AUTHENTICATION"]["USERNAME_REGEX"]) #TODO: Specify which regex had a problem and where, currently not verbose enough.
    re.compile(config["AUTHENTICATION"]["PASSWORD_REGEX"])

def validate_required_options(config):
    """
        Ensures that all of the required Predict config options and sections are present in the
        configuration file.

        Args:
            the configuration object to check 
    """
    actual_secs = set(config.sections())
    required_secs = set(CONFIG_TEMPLATE.keys()) 
    if actual_secs != required_secs:
        raise configparser.Error("Missing Required Section(s): " + ", ".join(required_secs - expected_secs))

    # Then make sure the passed in config contains all the options it needs. # TODO: Maybe change this to the set diff thing, so we can see more missing options at once
    # in the error mesage.
    for section_name, section in CONFIG_TEMPLATE.items():
        for option in section.keys():
            if not config.has_option(section, option):
                raise configparser.Error("Missing option " + o + " from section " + s)

def validate_booleans(config):
    """
        Ensures that the Predict options that should be boolean, are.
    """
    try:
        config.getboolean("WHITELIST", "WHITELIST_ENABLED")
    except ValueError: # TODO: List suitable boolean values as specified by the get_boolean method of configparser.
         raise configparser.Error("The value of "+ config["WHITELIST"]["WHITELIST_ENABLED"] + " from section WHITELIST, option WHITELIST_ENABLED is not a suitable boolean value!")
    try:
        config.getboolean("SECURITY", "LOGIN_REQUIRED")
    except ValueError:
        raise configparser.Error("The value of "+ config["SECURITY"]["LOGIN_REQUIRED"] + " from section SECURITY option LOGIN_REQUIRED is not a suitable boolean value!")
  

def validate_whitelist(config):
    """
        Ensure the names in whitelist match the username regex pattern.
    """
    bad_names = []   
    for username in config["WHITELIST"]:
        if username != "WHITELIST_ENABLED":
            if not predict.auth.string_match(
                username, config["AUTHENTICATION"]["USERNAME_REGEX"]
            ):
                bad_names.append(username)
    if bad_names != []:
        raise configparser.Error(
                    "The username(s) {} do not conform to the regex '{}'".format(
                        bad_names, config["AUTHENTICATION"]["USERNAME_REGEX"]
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
    config.add_section("SECURITY")
    config.add_section("AUTHENTICATION")
    config.add_section("DATABASE")

    config.set("WHITELIST", "; " + WHITELIST_INFO[0])
    config.set("WHITELIST", "; " + WHITELIST_INFO[1])
    config.set("WHITELIST", "; " + WHITELIST_INFO[2])

    config.set("SECURITY", "; " + SECURITY_INFO[0])
    config.set("SECURITY", "; " + SECURITY_INFO[1])

    config.set("AUTHENTICATION", "; " + AUTH_INFO)
    
    config.set("DATABASE", "; " + DB_INFO)

    config.read_dict(CONFIG_TEMPLATE)
   
    return config
