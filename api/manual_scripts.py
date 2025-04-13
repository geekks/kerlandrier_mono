# TO DO: launch differents scripts from this main file with prompt or arguments

from script.import_ics import import_ics
from script.configuration import config


import_ics(config.ICS_PRIVATE_URL_KLR_FB.get_secret_value())