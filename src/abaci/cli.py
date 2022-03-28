import argparse
import logging
import os
from os.path import exists, join
import multiprocessing
from abaci.utils import relpathshort

def abaci_cli():
    """Defines the command line interface parser"""

    parser = argparse.ArgumentParser(prog='abaci',
                description='Utility for compiling and running abaqus jobs with user subroutines',
                usage='abaci [job-spec] [optional arguments]',
                epilog="""On execution, abaci will look for and parse an 'abaci.toml' configuration file
                          in the current working directory, unless an alternative path  has been specified
                           via the '--config' option. Abaci will then compile the user subroutine and
                           launch one or more abaqus jobs as specified by the 'job-spec' argument.
                           If no job-spec is given, then all jobs with the 'default' tag are run.
                           Regression checks are performed at the end for those jobs with checks specified.
                           """)
    
    parser.add_argument(metavar='job-spec',dest='job_spec',type=str,nargs='?',default='default',
                          help='Either: a comma-separated list of job tags or jobs names to filter jobs'
                                ' specified in the manifest; OR a path to an abaqus job file to run.')

    parser.add_argument('-V','--version',help='show abaci version',
                        dest='show_version',action='store_true')

    verbose_group = parser.add_mutually_exclusive_group()

    verbose_group.add_argument('-v','--verbose',help='output more information from abaci',
                        dest='verbose',action='count',default=0)
    
    verbose_group.add_argument('-q','--quiet',help='output less information from abaci',
                        dest='verbose',action='store_const',const=-1)

    parser.add_argument('-e','--echo',help='parse and display the config file, then stop',
                        dest='echo',action='store_true',default=False)

    parser.add_argument('-l','--list',help='list jobs specified in config file, then stop',
                        dest='list',action='store_true',default=False)

    parser.add_argument('-t','--codecov',help='compile subroutines for code coverage analysis',
                        dest='codecov',action='store_true')

    parser.add_argument('-d','--debug',help='compile with debug flags',
                        dest='debug',action='store_true')

    parser.add_argument('-0','--noopt',help='compile without any optimisations',
                        dest='noopt',action='store_true')

    parser.add_argument('-c','--compile',help='compile only, don\'t run abaqus',
                        dest='compile',action='store_true')

    parser.add_argument('-b','--background',help='run abaci in the background after compilation',
                        dest='background',action='store_true')

    parser.add_argument('--config',type=str,help='specify a different config file to default ("abaci.toml")',
                        dest='config',default='abaci.toml')

    parser.add_argument('-n','--nproc',type=int,help='specify number of threads/processes to run with Abaqus',
                        dest='nproc',default=1)

    parser.add_argument('-j','--jobs',type=int,help='run jobs concurrently, optionally specify a maximum number of concurrently running jobs',
                        nargs='?',dest='njob',action='store',const=None,default=1)

    return parser


def parse_cli():
    """Parses the command line inputs and returns the resulting namespace"""

    parser = abaci_cli()

    args = parser.parse_args()

    if args.show_version:
        print('Abaci version 0.1.0 (alpha)')
        exit()

    args.verbose = min(args.verbose,2)

    
    if args.background:

        # Background not support on Windows
        if os.name == 'nt':
            print(' (!) Background execution (-b/--background) is not supported on Windows.')
            exit(1)

        # No screen output if going into the background
        args.verbose = -1

    # Normalise the job-spec into a list
    if ',' in args.job_spec:
        args.job_spec = args.job_spec.split(',')
    else:
        args.job_spec = [args.job_spec]

    # Use number of CPUs if value not given for jobs
    if not args.njob:
        args.njob = multiprocessing.cpu_count()

    return args


def init_logger(verbose):
    """Initialise the abaci global logger"""

    if verbose > 0:
        log_fmt = '%(levelname)8s: %(message)s'
    else:
        log_fmt = ' %(message)s'

    log = logging.getLogger('abaci')
    log.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(10*(2-verbose))
    stream_handler.setFormatter(logging.Formatter(log_fmt))

    log.addHandler(stream_handler)

    log.debug('Verbosity is %s',verbose)


def new_log_filename(log_dir):
    """Get a new unused file name for log"""

    stem = join(log_dir, "abaci-{counter}.log")

    counter = 0

    while exists(stem.format(counter=counter)):

        counter = counter + 1

    return stem.format(counter=counter)


def init_logger_file(log_dir):
    """Add a file handler to global logger"""

    log = logging.getLogger('abaci')

    log_file = new_log_filename(log_dir)

    fmt = ' %(asctime)s %(levelname)8s: %(message)s'

    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(fmt))

    log.addHandler(handler)

    log.debug('Starting file log')
    log.info('Log file for this session is "%s"',relpathshort(log_file))
