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

config_template = {
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
        except re.error as e:
            print(e)
        except configparser.Error as e:
            # If there is a malformed config, print a general error message, and do not let the application continue.
            import sys
            print("Configuration file is located at: " + file_path)
            print("Predict Configuration Error: {}".format(e))
            sys.exit(1)
        return config

    return None  # Otherwise return None, because there is no config at given location


def validate_config(config):
    """
        Validates a given configuration file, by ensuring the required predict whitelist options and
        headers are present, the given regexes compile, .

        Args:
            config: the configuration object to validate
    """

   
    validate_required_options(config)
    validate_regex(config)
    validate_booleans(config)

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

def validate_regex(config):
    """
        Compiles the config's regex patterns to check they are valid.

        Args:
            the configuration object whose regex to validate

        Raises:
            re.error if the regex is invalid.
    """
    re.compile(config["AUTHENTICATION"]["USERNAME_REGEX"])
    re.compile(config["AUTHENTICATION"]["PASSWORD_REGEX"])

def validate_required_options(config):
    """
        Ensures that all of the required Predict config options and sections are present in the
        configuration file.

        Args:
            the configuration object to check 
    """
    # Raises an error with a message containing the sections present in the template, but not present in 
    # the actual config
    template_secs = list(config_template.keys()) 
    if config.sections() != template_secs:
        raise configparser.Error("Missing section(s): " + str(set(template_secs).difference(config.sections())))
    

def validate_booleans(config):
    """
        Ensures that the options that should be boolean, are.
    """
    pass

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

    print(config_template)
    config.read_dict(config_template)
   
    config.set("WHITELIST", "; " + WHITELIST_INFO[0])
    config.set("WHITELIST", "; " + WHITELIST_INFO[1])
    config.set("WHITELIST", "; " + WHITELIST_INFO[2])

    config.set("SECURITY", "; " + SECURITY_INFO[0])
    config.set("SECURITY", "; " + SECURITY_INFO[1])

    config.set("AUTHENTICATION", "; " + AUTH_INFO)
    
    config.set("DATABASE", "; " + DB_INFO)

    return config
