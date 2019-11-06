import configparser
import os



#TODO: See how much of this can be shuttled into cli.py, if anything

'''
    Helper file for configuration work. NOTE: thought about making this a class, but there will only ever be one instance
    of this script run for an instance of predict app running and if you import this file it will create the config object 
    similarly to how one would do with a constructor
'''

#Create parsing object for manipulating config file
config = configparser.ConfigParser(allow_no_value=True)

#TODO: Transform into a constructor since we have instance variables that we want to be created ahead of time that are shared across functions?
def create_default_config():
    #By default the configuration file is an empty whitelist with basic username and password requirements
    config['whitelist'] = {}
    config.set('whitelist', '''#Please place the usernames of researchers allowed on the predict system in the below section. Each name should appear on a seperate 
    #line and do not requre values (=). ''')

    config['auth_settings']= {}
    config.set('auth_settings', ';control how strictly defined password and usernames are by modifying the regex in the below section')
    config['auth_settings'] = {'username_regex': '\\w+', 'password_regex': '\\w{8,}', 'secret_key': 'XXX'} #TODO: Figure out where the flask-login secret key is currently kept
    
    #TODO: Make it so the config file writes to a different directory, and creates it if it doesnt exist? Where on the admins computer should the config file be created?
    #There is currently only a singe config file inside.s

    if not os.path.isdir('configs'):
        os.mkdir('configs')

    #Write the file
    with open('configs/config.ini', 'w') as configfile:
        config.write(configfile)

def get_whitelist():
    '''
        Returns: A list containing strings representations of usernames from the configuration file
    '''
    return list(config._sections['whitelist'].keys())

create_default_config()

#TODO: Delete this DEBUGGING
#print (get_whitelist())