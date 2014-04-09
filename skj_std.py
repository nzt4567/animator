#!/usr/bin/env python
''' Global variables and basic functions used in the whole project '''

# AUTHOR
__author__ = "nzt4567"
__email__ = "nzt4567@gmx.com"
__status__ = "Finished"
__version__ = "0.2"
__license__ = "GPL"
__year__ = "2012/2013"
__maintainer__ = __author__
#
#                                                         GLOBALS (START)
#
temp_directories = {"root": "", "gnuplot": "", "source": ""}
allowed_effects = {"scheme": ["white", "black"], "size": ["xga", "hd"]}
arguments_defaults = dict()
arguments_values = dict()
arguments_repeatable = ("criticalvalue", "gnuplotparams", "effectparams")
exit_codes = {"SUCCESS": 0, "CLINE_ARG_PARSE": 10,
              "CNF_DIR_PARSE": 20, "ARGS_ERR_CHECK": 30,
              "REQ_CMD_MISS": 40, "TEMP_DIR_CREATE": 90,
              "SET_FILE_PROPERTIES": 50, "SET_ANIM_PROPERTIES": 60,
              "DRAW_ANIM_FRAMES": 70, "CREATE_ANIM": 80}
#
#                                                         GLOBALS (END)
#
#-----------------------------------------------------------------------------------------------------------------------
#
#                                                         FUNCTIONS (START)
#


def create_error_msg(type_, value_, ignorable_=True):
    ''' Create and return error message in universal format.
            status: finished
            return: str
    '''
    from sys import argv
    from os.path import split

    error_types = {"PYTHON": "original python error",
                   "TEMP_DIR_NOT_EXIST": "temporary directory expected to exist but it doesn't",
                   "TEMP_DIR_ALREADY_EXISTS": "temporary directory already exists, try to delete it manually",
                   "INTERNAL": "this seems like a serious internal bug, I am really sorry about this",
                   "INF_OR_NAN": "value is inf/nan in a place where actual number should be",
                   "INVALID_SYNTAX": "simply, something is wrong with the syntax of this",
                   "NO_SOURCE": "no valid source file",
                   "INVALID_VALUE": "this value you entered seems to be wrong",
                   "TOO_SMALL_ANIM": "speed/fps is < 1 => anim generating would take too long, " + \
                   "use -E for correcting to defaults",
                   "OUTPUT_DIR_CREATE": "cannot create output directory, " + \
                   "use -E for storing output in OS temp files"}

    if arguments_values['ignoreerrors'] and ignorable_ == True:
        err_level = "ignored error"
    else:
        err_level = "fatal error"

    err_prog = split(argv[0])[1]
    err_type = error_types[type_]
    err_value = value_
    return "[ERROR] {0}: {1}: {2}: \'{3}\'".format(err_prog, err_level, err_type, err_value)


def create_info_msg(info_):
    ''' Create and return info message in universal format.
            status: finished
            return: str
    '''
    return "[INFO] {0}".format(info_)


def create_debug_msg(func_, cmnd_, var_):
    ''' Create and return debug message in universal format.
            status: devel - is not really used anywhere
            return: str
    '''
    debug_command = {"check_file()": {"open": "with open( file_, mode = \"r\", encoding = \"utf-8\" ) as fd:"}}

    dbg_func = func_
    dbg_cmnd = debug_command[dbg_func][cmnd_]
    dbg_var = var_

    return "[DEBUG] {0} | [COMMAND]: \'{1}\' | [VAR]: \'{2}\'".format(dbg_func, dbg_cmnd, dbg_var)


def print_msg_verbose(debug_=None, info_=None, err_=None):
    ''' Provide unified way to print error/info/debug messages.
            status: finished
            return: None
    '''
    if arguments_values['verbose'] == 0:
        return

    if err_ != None and arguments_values['verbose'] >= 1 and arguments_values['ignoreerrors'] == True:
        print(err_)

    if info_ != None and arguments_values['verbose'] >= 1:
        print(info_)

    if debug_ != None and arguments_values['verbose'] >= 2:
        print(debug_)


def download_url(url_, store_url_to_, ignorable_=True):
    ''' Download url_, store it to temp_directories
            status: finished
            return: full path to temp_file / None
    '''
    from os.path import isdir
    if not isdir(store_url_to_):  # If directory for storing the url doesn't exist raise an exception
        raise OSError(create_error_msg("TEMP_DIR_NOT_EXIST", store_url_to_, False))

    from tempfile import mkstemp
    temp_file = mkstemp(dir=store_url_to_)  # Create temp file which will store downloaded data

    from os import fdopen
    from urllib.request import urlopen
    from urllib.request import URLError
    try:  # Download file from url_, store it localy in temp_file which is in store_url_to_
        with urlopen(url_) as url_response, fdopen(temp_file[0], mode="wb") as out_file:
            from shutil import copyfileobj
            copyfileobj(url_response, out_file)

    except (URLError, ValueError, OSError) as exception_msg:  # some other error happened when trying to download
        if arguments_values['ignoreerrors'] and ignorable_ == True:
            print_msg_verbose(err_=create_error_msg("PYTHON", exception_msg))
            return None
        else:
            raise OSError(create_error_msg("PYTHON", exception_msg, False))
    else:
        return temp_file[1]  # File successfuly created, return it's name


def cleanup_temp_files():
    ''' Check if we have created any temp files and if yes, delete them
            status: finished
            return: None
    '''
    from shutil import rmtree
    from os import listdir

    try: 
        rmtree(temp_directories["gnuplot"], ignore_errors=True) # If this fails, then it is up to the OS
        rmtree(temp_directories["source"], ignore_errors=True)
        if listdir(temp_directories["root"]) == []: # If animation has been stored here then don't delete it
            rmtree(temp_directories["root"], ignore_errors=True) 
    except OSError as exception_msg:
        print(create_error_msg("INTERNAL", exception_msg))


def create_temp_files(overwrite_=True):
    ''' Create temp directories and store their names
            status: finished
            return: None
            raise: ValueError
    '''
    global temp_directories

    from os.path import isdir
    if isdir(temp_directories["root"]):
        if overwrite_:
            cleanup_temp_files()
        else:
            raise ValueError(create_error_msg("TEMP_DIR_ALREADY_EXISTS", temp_directories["root"], False))

    from sys import argv
    from os.path import split
    from tempfile import mkdtemp
    temp_directories["root"] = mkdtemp(suffix="__" + split(argv[0])[1], prefix="tmp__")

    for directory in temp_directories:
        if directory != "root":
            temp_directories[directory] = mkdtemp(suffix="__" + directory,
                                                  prefix="tmp__",
                                                  dir=temp_directories["root"])


def exit_with_failure(exit_msg_, exit_code_):
    ''' Print error message, try to clean temporary files and exit with correct exit code
            status: finished
            return: None
    '''
    print(exit_msg_)
    cleanup_temp_files()
    exit(exit_codes[exit_code_])


def exit_with_success():
    ''' Try to clean temporary files and exit with correct exit code
            status: finished
            return: None
    '''
    cleanup_temp_files()
    exit(exit_codes["SUCCESS"])
#
#                                                         FUNCTIONS (END)
#