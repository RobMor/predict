import configparser
import os
import random
import string


'''
    Helper file for configuration work.
'''

# Create parsing object for manipulating config file
config = configparser.ConfigParser(allow_no_value=True)
config.optionxform = str # Allows for uppercase keys so the flask-login will disable properly when it reads the configuration.

# TODO: Maybe have this function return the current config hash by default?
def create_default_config(arguments):
    '''
        Creates the configuration file in the default location of configs/config.ini. Fills the 
        configuration file with default regex and an empty whitelist and comments describing the 
        sections of the config.ini.

        Parameters:
            arguments: the arguments (presumably passed in from cli.py) from the command line.
    '''
    # By default the configuration file is an empty whitelist with basic username and password requirements.
    
    # TODO: Change these to config defaults?
   
    config['whitelist'] = {}
    config.set('whitelist', '''#Please place the usernames of researchers allowed on the predict system in the below section. 
#Each name should appear on a seperate line and do not requre values (=).''')
    
    # TODO: See if there is a faster way to add feilds without overriding. NOTE: Using config.set followed by config[] on the same section
    # clears that section.
    config['auth_settings']= {}
    config.set('auth_settings', ';Control how strictly defined password and usernames are by modifying the regex in the below section')

    config['auth_settings']['username_regex'] = '\\w+'
    config['auth_settings']['password_regex'] = '\\w{8,}'

    config['flask_login'] = {}
    config.set('flask_login','#Secret key is used to encrypt flask-login sessions. Only set it if you know what you are doing.')
    #config['flask_login']['SECRET_KEY'] = str(os.urandom(16)).replace('%','') #NOTE: Stricter version of secret keys
    config['flask_login']['SECRET_KEY']  = randomSecret(3)
    config['flask_login']['LOGIN_DISABLED'] = str(not arguments.secured)
    
    # TODO: Make it so the config file writes to the user's home directory unless environment variable set.
    write_config()

def randomSecret(stringLength):
    '''
        Generate a random string of fixed length
    '''
    letters = string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def write_config():
    '''
        Writes the config file and creates a new configs directory if one
        does not exist, already.
    '''
    if not os.path.isdir('configs'):
        os.mkdir('configs')

    with open('configs/config.ini', 'w') as configfile:
        config.write(configfile)

#TODO: Determine whether this needs to be filtering out the commented items inside the .ini file.
def get_whitelist():
    '''
        Returns: A list containing string representations of usernames from the configuration file
    '''
    return list(config._sections['whitelist'].keys())

#TODO: Determine whether or not need a helper function or this or can obtain it straight out of the import from the other class.
def get_config():
    '''
        Returns: The current confiiguration as a dictionary
    '''
    return config._sections
