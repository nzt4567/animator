#!/usr/bin/env python
''' Checker - check user input, existence of required programs, etc '''

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

#
#                                                         MISC (START)
#


def check_command_exists(command_, ignorable_=True):
    ''' Check for command_ existence && executability
        status: finished
        return: command_ / None
        raise: OSError
    '''
    import subprocess
    try:
        subprocess.call(command_, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, timeout=5)
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError, ValueError, TypeError) as exception_msg:
        if skj_std.arguments_values['ignoreerrors'] and ignorable_ == True:
            skj_std.print_msg_verbose(err_=skj_std.create_error_msg("PYTHON", exception_msg))
            return None
        else:
            raise OSError(skj_std.create_error_msg("PYTHON", exception_msg, False))
    else:
        return command_


def check_time_format(datetime_, ignorable_=True, verbose_=True):
    ''' Check if string containing date and time is in the specified format.
        status: finished
        return: time_struct / None
        raise: ValueError
    '''
    from time import strptime
    try:
        ret = strptime(datetime_[0], datetime_[1])
    except (ValueError, TypeError, IndexError) as exception_msg:
        if skj_std.arguments_values['ignoreerrors'] and ignorable_ == True:
            skj_std.print_msg_verbose(err_=skj_std.create_error_msg("PYTHON", exception_msg))
            return None
        else:
            raise ValueError(skj_std.create_error_msg("PYTHON", exception_msg, False))
    else:
        return ret


def check_float_ok(float_, ignorable_=True, verbose_=True):
    ''' Check if string is float and not inf/nan
        status: finished
        return: float / None
        raise: ValueError
    '''
    from math import isinf, isnan
    try:
        if isnan(float(float_)) or isinf(float(float_)):
            raise ValueError("value is inf/nan in a place where actual number should be")
    except (ValueError, TypeError) as exception_msg:
        if skj_std.arguments_values['ignoreerrors'] and ignorable_ == True:
            skj_std.print_msg_verbose(err_=skj_std.create_error_msg("PYTHON", exception_msg))
            return None
        else:
            raise ValueError(skj_std.create_error_msg("PYTHON", exception_msg, False))
    else:
        return float(float_)


def check_file(file_, ignorable_=True, verbose_=True):
    ''' Check if file exists && is readable && not empty
        status: finished
        return: file_ / None
        raise: IOError
    '''
    try:
        with open(file_, mode="r", encoding="utf-8") as f: # If file exists && is readable...
            from os.path import isfile 
            if not isfile(file_): # ... && is a normal file (no block device, etc) ...
                raise OSError("File " + file_ + " is not a regular file")

            from os import stat
            if stat(f.fileno()).st_size <= 0: # ... && is not empty ... 
                raise OSError("File " + file_ + " is empty")

            f.readline() # ... && is really an unicode file ... 
    except (IOError, TypeError, OSError, UnicodeDecodeError) as exception_msg:
        if skj_std.arguments_values['ignoreerrors'] and ignorable_ == True:
            skj_std.print_msg_verbose(err_=skj_std.create_error_msg("PYTHON", exception_msg))
            return None
        else:
            raise IOError(skj_std.create_error_msg("PYTHON", exception_msg, False))
    else:
        return file_  # ... then it has passed all basic tests

#
#                                                         MISC (END)
#
# -------------------------------------------------------------------------------------------------------------------- #
#
#                                                         USER INPUT (START)
#


def check_effects_syntax():
    ''' Check for allowed syntax
        status: finished
        return: dict
        raise: ValueError
    '''
    valid_effects = dict()

    f = skj_std.arguments_values['effectparams'] # wtf is this mess, right?
    u = [l.split(":") for l in f] # well, if I'll ever want to piss someone in team...
    c = [f for l in u for f in l] # ... i'll play on stubborn, selfish asshole ...
    k = [f.split("=") for f in c] # ... and write my code just like folks at MFF ...
    _ = {e[0]:e[1] for e in k if len(e) > 1} # ... write math!

    parsed_effects = _ # ouky douky, lets get back to work
    for effect in parsed_effects:
        if effect in skj_std.allowed_effects:
            if parsed_effects[effect] in skj_std.allowed_effects[effect]:
                valid_effects[effect] = parsed_effects[effect]
                continue

        if skj_std.arguments_values['ignoreerrors']:
            skj_std.print_msg_verbose(err_=skj_std.create_error_msg("INVALID_VALUE", effect))
        else:
            raise ValueError(skj_std.create_error_msg("INVALID_VALUE", effect))

    return valid_effects


def check_x(type_, default_):
    ''' Check if string is "auto"/"max/min"/time_string.
        status: finished
        return: None
        raise: ValueError
    '''
    if type_ == "max":  # As we are checking for two values, we have to decide which one is it now first
        to_check = skj_std.arguments_values['xmax']
    elif type_ == "min":
        to_check = skj_std.arguments_values['xmin']
    else:  # This should really never happen, but just to be sure
        raise ValueError(skj_std.create_error_msg("INTERNAL", to_check, False))

    if to_check == "auto" or to_check == default_:
        return  # Problem solved, value is not in date-time format

    if not check_time_format((to_check, skj_std.arguments_values['timeformat'])):
        if type_ == "max":
            skj_std.arguments_values['xmax'] = default_
        else:
            skj_std.arguments_values['xmin'] = default_


def check_y(type_, default_):
    ''' Check if string is "auto"/"max/min"/float.
        status: finished
        return: None
        raise: ValueError
    '''
    if type_ == "max":  # As we are checking for two values, we have to decide which one is it now first
        to_check = skj_std.arguments_values['ymax']
    elif type_ == "min":
        to_check = skj_std.arguments_values['ymin']
    else:  # This should really never happen, but just to be sure
        raise ValueError(skj_std.create_error_msg("INTERNAL", to_check, False))

    if type_ == to_check or to_check == default_:
        return  # Problem solved, value is max/min/default

    if check_float_ok(to_check) == None:
        if type_ == "max":
            skj_std.arguments_values['ymax'] = default_
        else:
            skj_std.arguments_values['ymin'] = default_


def check_critical_value():
    ''' Check for allowed syntax - viz edux
        status: finished
        return: dict
        raise: ValueError
    '''
    crit_values = {'x': [], 'y': []}

    for value in skj_std.arguments_values['criticalvalue']:
        if len(value) >= 2:
            if (value[0] == 'x' or value[0] == 'y') and value[1] == '=':
                if value[0] == 'x':
                    if check_time_format((value[2:], skj_std.arguments_values['timeformat'])):
                        crit_values['x'].append(value[2:])
                else:
                    if check_float_ok(value[2:]) != None:
                        crit_values['y'].append(value[2:])

    return crit_values

def check_parsed_args():
    ''' Check arguments for different kinds of errors
        status: finished
        return: None
        raise: ValueError, OSError, IOError
    '''
    # Deduplicate parametrs stored in lists, while preserving their order (else list(set(x)))
    for argument in skj_std.arguments_repeatable:
        if skj_std.arguments_values[argument]:
            duplicate = set()
            skj_std.arguments_values[argument] = [x for x in skj_std.arguments_values[argument]\
                                                 if x not in duplicate and not duplicate.add(x)]
    duplicate = set()
    skj_std.arguments_values['source'] = [x for x in skj_std.arguments_values['source']\
                                         if x not in duplicate and not duplicate.add(x)]

    # Download files that are not local, store them in temp files
    for source in list(skj_std.arguments_values['source']):
        if source.lower().strip().startswith("http://") or \
           source.lower().strip().startswith("https://"):
            skj_std.arguments_values['source'].remove(source)  # Remove link from sources list
            skj_std.arguments_values['source'].append(skj_std.download_url(source, \
            skj_std.temp_directories['source'], False))
            source = skj_std.arguments_values['source'][-1]
        check_file(source, ignorable_=False) # this used to be in else clause

    # Check if -c parametr has correct syntax
    if skj_std.arguments_values['criticalvalue'] != skj_std.arguments_defaults['criticalvalue']:
        skj_std.arguments_values['criticalvalue'] = check_critical_value()
        if  len(skj_std.arguments_values['criticalvalue']['x']) == 0 and \
            len(skj_std.arguments_values['criticalvalue']['y']) == 0:
                skj_std.arguments_values['criticalvalue'] = skj_std.arguments_defaults['criticalvalue']


    # And the same for -x/-X/-y/-Y
    for value in ["ymax", "ymin", "xmax", "xmin"]:
        if value[0] == "x":
            check_x(value[1:], skj_std.arguments_defaults[value])
        else:
            check_y(value[1:], skj_std.arguments_defaults[value])

    # Well... and also for effects
    if skj_std.arguments_values['effectparams'] != skj_std.arguments_defaults['effectparams']:
        skj_std.arguments_values['effectparams'] = check_effects_syntax()
#
#                                                         USER INPUT (END)
#