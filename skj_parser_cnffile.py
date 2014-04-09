#!/usr/bin/env python
''' Parse config file directives '''

# IMPORTS
import skj_std

# AUTHOR
__author__ = skj_std.__author__
__email__ = skj_std.__email__
__status__ = skj_std.__status__
__version__ = skj_std.__version__
__license__ = skj_std.__license__
__year__ = skj_std.__year__
__maintainer__ = skj_std.__maintainer__


def add_directives_to_args(config_file_, repeatable_directives_):
    ''' Add arguments that were unspecified on cmd-line but present in cnf-file
            status: finished
            return: None
            raise: None
    '''
    # Check every argument we know (cmd line has already been parsed)
    for argument in skj_std.arguments_values:
        if argument in config_file_:  # Was this option configured using config file ?
            # And it wasn't configured using cmd line ?
            if skj_std.arguments_values[argument] == skj_std.arguments_defaults[argument]:
                skj_std.arguments_values[argument] = config_file_[argument]  # Use the value from config file
            # If it isn't option from those which can be repeated it has to be on cmd
            elif argument in repeatable_directives_:  
                # And if it is repeatable, add it to the valid options dict
                skj_std.arguments_values[argument] += config_file_[argument]


def parse_directives():
    ''' Parse configuration file directives
            status: finished
            return: None
            raise: IOError
    '''
    config_file = dict()

    for argument in skj_std.arguments_repeatable:
        config_file[argument] = list()

    try:
        with open(skj_std.arguments_values['config'], mode="r", encoding="utf-8") as cnf_file:
            for line in cnf_file:
                option = line.partition('#')[0].strip().split(None, 1)
                if len(option) > 0:
                    # Check if it is a valid directive 
                    if option[0].lower() not in skj_std.arguments_defaults:
                        raise ValueError(option[0] + " is not a configuration directive")
                    if len(option) == 1:
                        raise ValueError(option[0] + " does not have configuration value")
                    if option[0].lower() in ["speed", "fps", "time"]: # should be created as list of floats from argparse
                        from skj_checker_common import check_float_ok
                        option[1] = check_float_ok(option[1]) # Check && convert string to float if possible

                    # Store valid directives
                    if option[0].lower() in skj_std.arguments_repeatable:
                        config_file[option[0].lower()].append(option[1])
                    else:
                        config_file[option[0].lower()] = option[1]
    except (IOError, IndexError, TypeError, ValueError) as exception_msg:
        if skj_std.arguments_values['ignoreerrors']:
            skj_std.print_msg_verbose(err_=skj_std.create_error_msg("PYTHON", exception_msg))
            return
        else:
            raise IOError(skj_std.create_error_msg("PYTHON", exception_msg, False))
    else:
        add_directives_to_args(config_file, skj_std.arguments_repeatable)