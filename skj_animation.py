#!/usr/bin/env python
''' Process a set of frames using ffmpeg to create required animation '''

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

def get_anim_records():
    ''' Return number of lines for every source file 
        status: finished
        yield: int
        raise: None
    '''
    for source_file in skj_std.arguments_values['source']:
        yield source_file["num_of_lines"]

def create_speed_seq(file_, int_, frac_):
    ''' Create int sequence where each number represents count of lines to be added to gnuplot input  
        status: finished
        return: list
        raise: None
    '''
    from math import modf

    file_seq = list()
    frac_reminder = 0

    if frac_ == 0: # If the speed is integer, we could just return the quotient and reminder and not whole list...
        file_seq = [int_ for i in range(0, int(file_['num_of_lines'] / int_))]
        if file_['num_of_lines'] % int_ != 0: # ... which would save some time && memory
            file_seq.append(file_['num_of_lines'] % int_)
    else:
        while sum(file_seq) != file_['num_of_lines']:
            to_append = int_
            frac_reminder += frac_

            if frac_reminder >= 1:
                frac_reminder_frac  = modf(frac_reminder)[0]
                frac_reminder_natur = modf(frac_reminder)[1]
                frac_reminder -= frac_reminder_natur
                to_append += int(frac_reminder_natur)

            if sum(file_seq) + to_append <= file_['num_of_lines']:
                file_seq.append(to_append)
            else:
                file_seq.append(file_['num_of_lines'] - sum(file_seq))

    return file_seq


def determine_anim_type():
    ''' Decide whether animation is multiplot type or oneline
        status: finished
        return: str
        raise: IndexError
    '''
    try:
        time_max = skj_std.arguments_values['source'][0]
        time_min = skj_std.arguments_values['source'][0]
    except IndexError as exception_msg:
        raise IndexError(skj_std.create_error_msg("INTERNAL", exception_msg))

    for source_file in skj_std.arguments_values['source']:
        if source_file['time_min'] < time_min['time_min']:
            time_min = source_file
            if source_file['time_max'] >= time_max['time_max']:
                time_max = source_file # If the file with new min can also have new max, use it ...
        elif source_file['time_max'] > time_max['time_max']:
            time_max = source_file
            if source_file['time_min'] <= time_min['time_min']:
                time_min = source_file # ... because of correct anim type detection

    if time_max["path"] == time_min["path"] and len(skj_std.arguments_values['source']) != 1: # Hope this works 
        return "multiplot"
    return "oneline"


def calculate_sfft():
    ''' Calculate speed (num of records read each gnuplot iteration), fps, animation duration and num of frames
        status: devel - those if-chanins should be gone
        return: None
        raise: ValueError, ArithmeticError
    '''
    # 0. No user input
    # 1. User speed && fps
    # 2. User speed
    # 3. User fps
    if  (skj_std.arguments_values['time'] == skj_std.arguments_defaults['time'] and\
        skj_std.arguments_values['speed'] == skj_std.arguments_defaults['speed'] and\
        skj_std.arguments_values['fps'] == skj_std.arguments_defaults['fps']) or\
        (skj_std.arguments_values['speed'] != skj_std.arguments_defaults['speed'] and\
        skj_std.arguments_values['fps'] != skj_std.arguments_defaults['fps'] and\
        skj_std.arguments_values['time'] == skj_std.arguments_defaults['time']) or\
        (skj_std.arguments_values['speed'] != skj_std.arguments_defaults['speed'] and\
        skj_std.arguments_values['fps'] == skj_std.arguments_defaults['fps'] and\
        skj_std.arguments_values['time'] == skj_std.arguments_defaults['time']) or\
        (skj_std.arguments_values['speed'] == skj_std.arguments_defaults['speed'] and\
        skj_std.arguments_values['fps'] != skj_std.arguments_defaults['fps'] and\
        skj_std.arguments_values['time'] == skj_std.arguments_defaults['time']):
            # Calculate animation time
            try:
                skj_std.arguments_values['time'] = skj_std.arguments_values['records'] / \
                (skj_std.arguments_values['speed'] * skj_std.arguments_values['fps'])
            except (ArithmeticError, ZeroDivisionError) as exception_msg:
                raise ArithmeticError(skj_std.create_error_msg("PYTHON", exception_msg))

    # 0. User speed && time
    # 1. User time
    elif (skj_std.arguments_values['speed'] != skj_std.arguments_defaults['speed'] and\
        skj_std.arguments_values['fps'] == skj_std.arguments_defaults['fps'] and\
        skj_std.arguments_values['time'] != skj_std.arguments_defaults['time']) or\
        (skj_std.arguments_values['speed'] == skj_std.arguments_defaults['speed'] and\
        skj_std.arguments_values['fps'] == skj_std.arguments_defaults['fps'] and\
        skj_std.arguments_values['time'] != skj_std.arguments_defaults['time']):
            # Calculate animation fps
            try:
                skj_std.arguments_values['fps'] = skj_std.arguments_values['records'] / \
                (skj_std.arguments_values['speed'] * skj_std.arguments_values['time'])
            except (ArithmeticError, ZeroDivisionError) as exception_msg:
                raise ArithmeticError(skj_std.create_error_msg("PYTHON", exception_msg))

    # User time && fps
    elif skj_std.arguments_values['speed'] == skj_std.arguments_defaults['speed'] and\
        skj_std.arguments_values['fps'] != skj_std.arguments_defaults['fps'] and\
        skj_std.arguments_values['time'] != skj_std.arguments_defaults['time']:
            # Calculate animation speed
            try:
                skj_std.arguments_values['speed'] = skj_std.arguments_values['records'] / \
                (skj_std.arguments_values['fps'] * skj_std.arguments_values['time'])
            except (ArithmeticError, ZeroDivisionError) as exception_msg:
                raise ArithmeticError(skj_std.create_error_msg("PYTHON", exception_msg))

    # User time && speed && fps
    elif skj_std.arguments_values['time'] != skj_std.arguments_defaults['time'] and\
        skj_std.arguments_values['speed'] != skj_std.arguments_defaults['speed'] and\
        skj_std.arguments_values['fps'] != skj_std.arguments_defaults['fps']:
            # Calculate correct time
            try:
                time_check = skj_std.arguments_values['records'] / \
                (skj_std.arguments_values['speed'] * skj_std.arguments_values['fps'])
            except (ArithmeticError, ZeroDivisionError) as exception_msg:
                raise ArithmeticError(skj_std.create_error_msg("PYTHON", exception_msg))

            # Check if correct time matches user time
            if time_check != skj_std.arguments_values['time']:
                if skj_std.arguments_values['ignoreerrors']:
                    skj_std.print_msg_verbose(err_=skj_std.create_error_msg("INVALID_VALUE", \
                                                                           skj_std.arguments_values['time']))
                    skj_std.arguments_values['time'] = time_check
                else:
                    raise ValueError(skj_std.create_error_msg("INVALID_VALUE", skj_std.arguments_values['time']))

    from math import ceil
    skj_std.arguments_values['frames'] = ceil(skj_std.arguments_values['records'] / skj_std.arguments_values['speed'])


def set_animation_properties():
    ''' Set properties of animation like speed, time, num of frames, num of records, type, etc
        status: finished
        return: None
        raise: TypeError, IndexError, ValueError
    '''
    # Get animation type
    skj_std.arguments_values['animation_type'] = determine_anim_type() # raise IndexError

    # Then calculate the number of valid lines (valid line is also called 'record')
    skj_std.arguments_values['records'] = 0 # File with zero records should never exist
    for lines_file in get_anim_records():
        if skj_std.arguments_values['animation_type'] == "multiplot":
            # Multiplot animation has as many records as the longest file has lines
            if lines_file > skj_std.arguments_values['records']:
                skj_std.arguments_values['records'] = lines_file
        else:
            # Oneline animation has sum(all_lines) records
            skj_std.arguments_values['records'] += lines_file

    # Calculate correct speed && fps && frames && time
    calculate_sfft() # raise VauleError, ArithmeticError (catch AE? => if ignoreerrors: speed = 0 (see code below))
    
    # Correct speed/fps if it is too low (< 1), cause that leads to crazy long create_speed_seq() && generate_anim()
    if skj_std.arguments_values['speed'] < 1 or skj_std.arguments_values['fps'] < 1:
        if skj_std.arguments_values['ignoreerrors']:
            skj_std.print_msg_verbose(err_=skj_std.create_error_msg("TOO_SMALL_ANIM", \
                                     str(skj_std.arguments_values['speed']) + \
                                     "/" + str(skj_std.arguments_values['fps'])))
            skj_std.arguments_values['speed'] = skj_std.arguments_defaults['speed']
            skj_std.arguments_values['fps'] = skj_std.arguments_defaults['fps']
            skj_std.arguments_values['time'] = skj_std.arguments_defaults['time']
            calculate_sfft()
        else:
            raise ValueError(skj_std.create_error_msg("TOO_SMALL_ANIM", \
                            str(skj_std.arguments_values['speed']) + "/" + str(skj_std.arguments_values['fps'])))

    # Create sequence of records added to every created frame
    from math import modf
    try: # Divide the speed on it's integer and fractional parts
        speed_fraction = modf(skj_std.arguments_values['speed'])[0]
        speed_integer = int(modf(skj_std.arguments_values['speed'])[1])
    except TypeError as exception_msg:
        raise TypeError(skj_std.create_error_msg("INTERNAL", exception_msg))
    for source_file in skj_std.arguments_values['source']: # Add the sequence to each file's properties
        source_file['adding_seq'] = create_speed_seq(file_=source_file, int_=speed_integer, frac_=speed_fraction)


def create_animation():
    ''' Finally, call ffmpeg and let it do it's magic
        status: finished
        return: None
        raise: OSError
    '''
    import os
    import subprocess
    from sys import argv

    if skj_std.arguments_values['name'] == skj_std.arguments_defaults['name']:
        skj_std.arguments_values['name'] = os.path.split(argv[0])[1]
    output = os.path.join(os.getcwd(), skj_std.arguments_values['name']) # Output directory

    if os.path.isdir(output):
        i = 0 # If the dir already exists ...
        output = output + '_' + str(i)
        while os.path.isdir(output):
            i += 1 # ... try output_i where i = max(i,0) + 1
            output = output[:output.rfind('_')] + '_' + str(i)

    try:
        os.makedirs(output) # If we do not have write/execute in os.getcwd()...
    except OSError as exception_msg:
        if skj_std.arguments_values['ignoreerrors']:
            skj_std.print_msg_verbose(err_=skj_std.create_error_msg("OUTPUT_DIR_CREATE", output))
            output = skj_std.temp_directories['root'] # ... move output to temp dir we already have ...
        else: # ... or die!
            raise OSError(skj_std.create_error_msg("OUTPUT_DIR_CREATE", output))

    filetype = ".mp4"
    codec  = "libx264"
    ffmpeg = ["ffmpeg", "-f", "image2", "-r", str(skj_std.arguments_values['fps']), "-i", \
              os.path.join(skj_std.temp_directories['gnuplot'], "g_%0" + \
              str(len(str(skj_std.arguments_values['frames']))) + "d.png"),
              "-c:v", codec, "-r", str(skj_std.arguments_values['fps']), \
               os.path.join(output, skj_std.arguments_values['name'].split('/')[-1]) + filetype]
    try:
        subprocess.check_call(ffmpeg, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as exception_msg:
        raise OSError(skj_std.create_error_msg("PYTHON", exception_msg))