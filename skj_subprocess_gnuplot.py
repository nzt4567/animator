#!/usr/bin/env python
''' Create a set of frames using gnuplot from user submitted data files'''

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


def set_file_properties(file_, datetime_format_=skj_std.arguments_values['timeformat']):
    ''' Get number of lines, min/max time value, min/max data and check time formatting on every line
        status: finished
        raise: ValueError
        return: dict / None
    '''
    with open(file_, mode="r", encoding="utf-8") as f:
        first_line = f.readline() # Read first line

        while first_line.isspace(): # Skip lines containing only whitespaces
            first_line = f.readline()
        if first_line == '': # Skip files containing only whitespaces
            return None

        num_of_lines = 1  # First line is read for setting first_line/time_max before the loop
        first_line = first_line.strip() # Remove trailing/foregoing whitespaces

        # Default values for date/data min/max are the values of first record
        from skj_checker_common import check_time_format, check_float_ok
        data_min = check_float_ok(first_line[first_line.rfind(' '):].strip(), False) # Last fields belongs to data
        data_max = data_min 
        time_min = check_time_format((first_line[:first_line.rfind(' ')], datetime_format_), False)  # raise ValueError 
        time_max = time_min

        for one_line in f:
            if one_line.isspace(): # Skip lines containing only whitespaces
                continue

            num_of_lines += 1  # Count lines in file
            one_line = one_line.strip() # Prepare line for processing

            # Grab data(float) from record
            data_from_line = check_float_ok(one_line[one_line.rfind(' '):].strip(), False)
            date_from_line = check_time_format((one_line[:one_line.rfind(' ')], datetime_format_), False)

            # Find min/max in data
            data_max = max(data_max, data_from_line)
            data_min = min(data_min, data_from_line)

            # Find min/max in date
            time_max = max(time_max, date_from_line)
            time_min = min(time_min, date_from_line)

    return {"path": file_, "num_of_lines": num_of_lines, "time_min": time_min, "time_max": time_max, 
            "date_column": 1, "data_column": len(first_line.split()), "data_min": data_min,
            "data_max": data_max}


def set_file_name(base_of_name_=""):
    ''' Create unique file name each time called
        status: finished
        return: str
        raise: None
    '''
    for x in range(0, skj_std.arguments_values['frames']):
        num_of_zeroes = len(str(skj_std.arguments_values['frames'])) - len(str(x))
        yield base_of_name_ + "_" + num_of_zeroes * "0" + str(x) + ".png"


def create_output_command(filename_):
    ''' Create output command for given filename_
        status: finished
        return: str
        raise: None
    '''
    from os.path import join
    return "set output '" + join(skj_std.temp_directories['gnuplot'], filename_) + "'\n"

def configure_crit_values(x_color_="red", y_color="red"):
    ''' Draw lines for each critical value
        status: finished
        return: str
        raise: None
    '''
    configuration = ""
    
    for x_crits in skj_std.arguments_values['criticalvalue']['x']:
        configuration += 'set arrow from "' + x_crits + '", graph 0 to "' + x_crits + \
                         '", graph 1 nohead lc rgb "' + x_color_ + '"\n'

    for y_crits in skj_std.arguments_values['criticalvalue']['y']:
        configuration += 'set arrow from graph 0, first ' + y_crits + ' to graph 1, first ' + \
                         y_crits + ' nohead lc rgb "' + y_color + '"\n' 

    return configuration

def get_record_extremes(type_):
    ''' Get global date/data min/max. type_ can be "time" or "data"
        status: finished
        return: tuple
        raise: IndexError, ValueError
    '''
    try:
        minimum = skj_std.arguments_values['source'][0][type_ + '_min']
        maximum = minimum
    except (IndexError, KeyError) as exception_msg:
        raise IndexError(skj_std.create_error_msg("INTERNAL", exception_msg))

    for f in skj_std.arguments_values['source']:
        maximum = max(maximum, f[type_ + '_max'])
        minimum = min(minimum, f[type_ + '_min'])
        
    if type_ == "time":
        from time import strftime
        try:      
            maximum = strftime(skj_std.arguments_values['timeformat'], maximum)
            minimum = strftime(skj_std.arguments_values['timeformat'], minimum)
        except (ValueError, TypeError) as exception_msg:
            raise ValueError(skj_std.create_error_msg("INTERNAL", exception_msg))

    return maximum, minimum


def configure_xy_basics():
    ''' Add basic user submitted options and some defaults to gnuplot configuration
        status: finished
        return: str
        raise: IndexError, ValueError
    '''
    configuration  = 'set timefmt "' + skj_std.arguments_values['timeformat'] + '"\n'
    configuration += 'set xdata time\n'
    configuration += 'set grid\n'
    configuration += 'unset key\n'

    data_max, data_min = get_record_extremes(type_="data") # raise IndexError, ValueError 
    time_max, time_min = get_record_extremes(type_="time") # raise IndexError, ValueError

    for value in ["ymax", "ymin", "xmax", "xmin"]:
        if skj_std.arguments_values[value] == "auto":
            skj_std.arguments_values[value] = "*"
        elif skj_std.arguments_values[value] == "max":
            if value == "ymax":
                skj_std.arguments_values[value] = data_max
            else:
                skj_std.arguments_values[value] = '"' + time_max + '"'
        elif skj_std.arguments_values[value] == "min":
            if value == "ymin":
                skj_std.arguments_values[value] = data_min
            else:
                skj_std.arguments_values[value] = '"' + time_min + '"'

    configuration += 'set xrange [' + skj_std.arguments_values['xmin'] + \
                     ':' + skj_std.arguments_values['xmax'] + ']\n'
    configuration += 'set yrange [' + str(skj_std.arguments_values['ymin']) + \
                     ':' + str(skj_std.arguments_values['ymax']) + ']\n'
    # Here should be a fix, to display the red labels only if scheme has been selected
    configuration += 'set xlabel "Date && Time" textcolor rgb "#FF0000"\n'
    configuration += 'set ylabel "Values" textcolor rgb "#FF0000"\n'

    return configuration

def create_frames_oneline(process_, filename_, date_column_, data_column_):
    ''' Create animation frames for "oneline" plot type
        status: finished
        return: None
        raise: None
    '''
    gnuplot_data = str()
    file_lines = list()
    
    for source_file in skj_std.arguments_values['source']:
        with open(source_file['path'], encoding="utf-8", mode="r") as f:
            file_lines += f.readlines()
        if not file_lines[-1].endswith('\n'): # Same as with multiplot
            file_lines[-1] += '\n'

    from random import seed, shuffle
    seed()
    shuffle(file_lines)    

    for source_file in skj_std.arguments_values['source']:
        for number in source_file['adding_seq']:
        # len(adding_seq) = num_of_frames => for each frame ...
            for i in range(0, number):
            # ... add the number of records that should be added to this frame
                gnuplot_data += file_lines.pop()

            plot =  "plot '-' using " + date_column_ + ":" + data_column_ + "\n"

            process_.stdin.write(create_output_command(next(filename_)).encode())
            process_.stdin.write(plot.encode())
            process_.stdin.write(gnuplot_data.encode())
            process_.stdin.write("e\n".encode())


def create_frames_multiplot(process_, filename_, date_column_, data_column_):
    ''' Create animation frames for "multiplot" plot type
        status: finished
        return: None
        raise: None
    '''
    from random import seed, shuffle
    seed()

    for source_file in skj_std.arguments_values['source']:
    # This prepares files for processing
        with open(source_file['path'], encoding="utf-8", mode="r") as f:
            source_file['data_list'] = f.readlines() # Load every file's records into memory
        
        # Files without empty line at the EOF would fail otherwise
        if not source_file['data_list'][-1].endswith('\n'):
            source_file['data_list'][-1] += '\n'

        shuffle(source_file['data_list']) # Randomize those records
        source_file['data_str'] = str() # And prepare string those records will be moved to

    for i in range(0, skj_std.arguments_values['frames']):
    # This creates every single frame
        for source_file in skj_std.arguments_values['source']:
            if len(source_file['adding_seq']) != 0: # If this file still has records... 
                for i in range(0, source_file['adding_seq'].pop(0)): # ... add them to string passed to gnuplot
                    source_file['data_str'] += source_file['data_list'].pop() 

        # Start the plot command ... 
        plot =  "plot"
        for i in skj_std.arguments_values['source']: # ... create the command body ...
            plot += " '-' using " + date_column_ + ":" + data_column_ + ","
        plot = plot[:-1] + "\n" # ... and finish it

        process_.stdin.write(create_output_command(next(filename_)).encode())
        process_.stdin.write(plot.encode())
        for source_file in skj_std.arguments_values['source']:
            process_.stdin.write(source_file['data_str'].encode())
            process_.stdin.write("e\n".encode())


def set_scheme_lines(color_):
    ''' Generate commands setting line properties
        status: finished
        return: str
        raise: None
    '''
    black = ["#FFFFFF", "#00FF00", "#FFFF00", "#0000FF", "#FF00FF", "#00FFFF", "#FF4000"]
    white = ["#000000", "#008000", "#008080", "#404000", "#000080", "#400080", "#804000"]
    scheme = black # For color specifications see eg. http://www.tedmontgomery.com/tutorial/clrctgBL.html

    if color_ == "white":
        scheme = white

    i = 0
    for color in scheme:
        i += 1 # First line in gnuplot has number 1
        yield 'set linetype ' + str(i) + 'lc rgb "' + color + '"\n'

def configure_effects():
    ''' Set effects like background/line colors, animation size, etc
        status: finished
        return: str
        raise: None
    '''
    terminal = 'set terminal png font "arial,10"'
    if skj_std.arguments_values['effectparams'] == skj_std.arguments_defaults['effectparams']:
        return terminal + '\n' # Default with no effect configured

    if "size" in skj_std.arguments_values['effectparams']:
        resolutions = {"xga": "1024,768", "hd": "1920,1080"} # Make changes to skj_std too if editing
        resolution = ' size ' + resolutions[skj_std.arguments_values['effectparams']['size']] + ' '
    else:
        resolution = ' size 640,480 ' # Default size

    if "scheme" in skj_std.arguments_values['effectparams']:
        scheme = 'set border 15 lw 3 lc rgb "#FF0000"\n' # use red for axes, ..
        scheme += 'set xtics textcolor rgb "#FF0000"\n' # ... for xtics, ...
        scheme += 'set ytics textcolor rgb "#FF0000"\n' # ... for ytics, ...
        if "white" == skj_std.arguments_values['effectparams']['scheme']:
            background = ' background "white" '
            for line in set_scheme_lines("white"):
                scheme += line
        else:
            background = ' background "black" '
            for line in set_scheme_lines("black"):
                scheme += line
        scheme += 'set linetype cycle 7\n'
    else:
        background = scheme = str() # Default is no scheme = it's up to gnuplot
    
    return terminal + resolution + background + '\n' + scheme

def draw_animation_frames():
    ''' Confgure gnuplot and draw frames into temp dir 
        status: finished
        return: None
        raise: ValueError, IndexError
    '''
    import subprocess

    gnuplot_config = configure_effects()
    gnuplot_config += configure_xy_basics() # raise ValueError, IndexError

    if skj_std.arguments_values['criticalvalue']:
        gnuplot_config += configure_crit_values()

    if skj_std.arguments_values['legend']:
        gnuplot_config += 'set title "' + skj_std.arguments_values['legend'] + \
        '" textcolor rgb "#FF0000" ' + '\n'

    # USER GNUPLOT CONFIG MUST BE LAST (to make it possible to override defaults)
    if skj_std.arguments_values['gnuplotparams']:
        for gnuplot_user_param in skj_std.arguments_values['gnuplotparams']:
            gnuplot_config += gnuplot_user_param + "\n"

    with subprocess.Popen(["gnuplot"], stdin=subprocess.PIPE) as gnuplot:
        gnuplot.stdin.write(gnuplot_config.encode())
        file_name_gen = set_file_name("g")
   
        date = str(skj_std.arguments_values['source'][0]['date_column'])
        data = str(skj_std.arguments_values['source'][0]['data_column'])
        if skj_std.arguments_values['animation_type'] == "oneline":
            create_frames_oneline(gnuplot, file_name_gen, date, data)
        else:
            create_frames_multiplot(gnuplot, file_name_gen, date, data)

        gnuplot.stdin.write("quit\n".encode())