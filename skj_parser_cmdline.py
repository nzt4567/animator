#!/usr/bin/env python
''' Parse command line arguments '''

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
#                                                         ARGUMENTS PARSING (START)
#


def alter_args(parser_):
    ''' Do some most basic edits to user input and check for config file
        status: finished
        return: None
    '''
    # Store default values into a dict
    for argument in skj_std.arguments_values:
        skj_std.arguments_defaults[argument] = parser_.get_default(argument)

    # Verbose needs to be int
    if skj_std.arguments_values['verbose'] == skj_std.arguments_defaults['verbose']:
        skj_std.arguments_values['verbose'] = 0

    # Check if configuration file exists and is readable
    if skj_std.arguments_values['config'] != skj_std.arguments_defaults['config']:
        from skj_checker_common import check_file
        skj_std.arguments_values['config'] = check_file(skj_std.arguments_values['config']) # raise IOError


def parse_args():
    ''' Parse all command line arguments
        status: finished
        return: dictionary
    '''
    import argparse

    parser = argparse.ArgumentParser( description='''\
Animation creation script. Requires Python (http://python.org/).
For more information please see the documentation.''',
                                      epilog='''\
Semestral work for BI-SKJ (B122) @ CTU (https://www.cvut.cz/)
Pls report bugs (bugs, what's that?) to ''' + __email__ + '''
Created by: ''' + __author__ + '''; License: ''' + __license__ + '''; Year: ''' + __year__,
                                      add_help=False,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    data = parser.add_argument_group("Data files")
    glob = parser.add_argument_group("Global options")
    animation = parser.add_argument_group("Animation options")

    # -e EFFECT
    animation.add_argument('-e', '--effect', type=str, action='append', dest='effectparams',
                           help='''Effects to use in animation. \
                    See user doc for more info on this. (type: %(type)s, default: %(default)s)''')

    # source [source...]
    data.add_argument('source', type=str, nargs='+',
                      help='''Path to files with data to process. \
                    Can be a filesystem path or URL accessible using http protocol.''')

    # -t timeformat
    glob.add_argument('-t', '--time-format', type=str, default='[%Y-%m-%d %H:%M:%S]', dest='timeformat',
                      help='''Date && time format in source files. See \"man -s 3 strftime\" for syntax. \
                    (type: %(type)s, default: %(default)s)''')

    # -X auto/max/timeformat
    animation.add_argument('-X', '--x-max', type=str, default='max', dest='xmax',
                           help='''Maximum value for X-axis. Use \"auto\"/\"max\"/timeformat. \
                    (type: %(type)s, default: %(default)s)''')

    # -x auto/min/timeformat
    animation.add_argument('-x', '--x-min', type=str, default='min', dest='xmin',
                           help='''Minimum value for X-axis. Use \"auto\"/\"min\"/timeformat. \
                    (type: %(type)s, default: %(default)s)''')

    # -Y auto/max/float
    animation.add_argument('-Y', '--y-max', type=str, default='auto', dest='ymax',
                           help='''Maximum value for Y-axis. Use \"auto\"/\"max\"/float. \
                    (type: %(type)s, default: %(default)s)''')

    # -y auto/min/float
    animation.add_argument('-y', '--y-min', type=str, default='auto', dest='ymin',
                           help='''Minimum value for Y-axis. Use \"auto\"/\"min\"/float. \
                    (type: %(type)s, default: %(default)s)''')

    # -S SPEED
    animation.add_argument('-S', '--speed', type=float, default=1, dest='speed',
                           help='''Number of records used to create one frame. \
                    See user doc for more info on this. (type: %(type)s, default: %(default)s)''')

    # -T TIME
    animation.add_argument('-T', '--time', type=float, dest='time',
                           help='''Animation duration. \
                    See user doc for more info on this. (type: %(type)s, default: %(default)s)''')

    # -F FPS
    animation.add_argument('-F', '--fps', type=float, default=25, dest='fps',
                           help='''Number of frames/second. \
                    See user doc for more info on this. (type: %(type)s, default: %(default)s)''')

    # -c CRITICAL
    animation.add_argument('-c', '--critical', type=str, action='append', dest='criticalvalue',
                           help='''Highlighted value in animation. \
                    See user doc for more info on this. (type: %(type)s, default: %(default)s)''')

    # -l LEGEND
    animation.add_argument('-l', '--legend', type=str, dest='legend',
                           help='''Animation legend. \
                    (type: %(type)s, default: %(default)s)''')

    # -g GNUPLOT
    animation.add_argument('-g', '--gnuplot', type=str, action='append', dest='gnuplotparams',
                           help='''Arguments passed to gnuplot. Syntax is YOUR responsibility. \
                    (type: %(type)s, default: %(default)s)''')

    # -f CONFIG
    glob.add_argument('-f', '--config', type=str, dest='config',
                      help='''Path to configuration file. \
                    See user doc for more info on this. (type: %(type)s, default: %(default)s)''')

    # -n NAME
    glob.add_argument('-n', '--name', type=str, dest='name',
                      help='''Name of the animation. \
                    See user doc for more info on this. (type: %(type)s, default: %(default)s)''')

    # -E
    glob.add_argument('-E', '--ignore-errors', action='store_true', default=False, dest='ignoreerrors',
                      help='''Try to ignore non-fatal errors, just print warnings. \
                    (type: bool, default: %(default)s)''')

    # -h
    glob.add_argument('-h', '--help', action='help',
                      help='''Show this help and exit. See doc for more help.''')
    # -v
    glob.add_argument('-v', '--verbose', action='count',
                      help='''Be verbose. Use multiple times to be more verbose.''')
    # -V
    glob.add_argument('-V', '--version', action='version', version='%(prog)s v' + __version__,
                      help='''Print program version and exit.''')

    # Now we know about all possible params, so parse them from command line
    skj_std.arguments_values = vars(parser.parse_args())

    # Most basic edits/checks which need to be passed before parsing optional config file
    alter_args(parser) # raise IOError
#
#                                                         ARGUMENTS PARSING (END)
#
