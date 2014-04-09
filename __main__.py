#!/usr/bin/env python
''' BI-SKJ animation creation script '''

# ADD (one day)
# -w <outfile>
# -B big_files TRUE

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
#                                                         CORE (START)
#
from skj_parser_cmdline import parse_args
try:  # Firs of all, parse command line args, all later decisions are based on them
    parse_args()
except IOError as exception_msg:
    skj_std.exit_with_failure(exception_msg, "CLINE_ARG_PARSE")


from skj_checker_common import check_command_exists
try:  # Check dependencies, they are required
    check_command_exists(["gnuplot", "-V"], False)
    check_command_exists(["ffmpeg", "-version"], False)
except OSError as exception_msg:
    skj_std.exit_with_failure(exception_msg, "REQ_CMD_MISS")


try:  # Try to create temporary directories, they are mandatory for the script to continue
    skj_std.create_temp_files()
except ValueError as exception_msg:
    skj_std.exit_with_failure(exception_msg, "TEMP_DIR_CREATE")


try:  # Do we have a valid config file? Then parse it too
    if skj_std.arguments_values['config'] != skj_std.arguments_defaults['config']:
        from skj_parser_cnffile import parse_directives
        parse_directives()
except IOError as exception_msg:
    skj_std.exit_with_failure(exception_msg, "CNF_DIR_PARSE")


from skj_checker_common import check_parsed_args
try:  # If we have alived the user input so far, now do some REAL user input checks
    check_parsed_args()
except (OSError, IOError, ValueError) as exception_msg:
    skj_std.exit_with_failure(exception_msg, "ARGS_ERR_CHECK")


from skj_subprocess_gnuplot import set_file_properties
try:  # Convert simple list of file names to more complex structures containing file properties
    for source_file in list(skj_std.arguments_values['source']):
        file_properties = set_file_properties(source_file)
        skj_std.arguments_values['source'].pop(0)
        if file_properties != None: # This filters files with only whitespaces
            skj_std.arguments_values['source'].append(file_properties)
    if not skj_std.arguments_values['source']:
        raise ValueError(skj_std.create_error_msg("NO_SOURCE", skj_std.arguments_values['source'], False))
except ValueError as exception_msg:
    skj_std.exit_with_failure(exception_msg, "SET_FILE_PROPERTIES")


from skj_animation import set_animation_properties
try: # set animation properties (S/F/T, adding seq for each file, num of frames for each file, etc)
    set_animation_properties()
except (ValueError, IndexError, TypeError, ArithmeticError) as exception_msg:
    skj_std.exit_with_failure(exception_msg, "SET_ANIM_PROPERTIES")


from skj_subprocess_gnuplot import draw_animation_frames
try: # Do not forget that this deletes the whole adding_seq for each file if type multiplot ...
    draw_animation_frames() # ... but that is okay, it will no longer be needed
except (IndexError, ValueError) as exception_msg:
    skj_std.exit_with_failure(exception_msg, "DRAW_ANIM_FRAMES")

from skj_animation import create_animation
try:
    create_animation()
except OSError as exception_msg:
    skj_std.exit_with_failure(exception_msg, "CREATE_ANIM")

skj_std.exit_with_success()

#
#                                                         CORE (END)
#
