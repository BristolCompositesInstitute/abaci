import argparse
import logging
import os
from os.path import exists, join
import multiprocessing
from abaci.utils import relpathshort

def parse_cli():
    """Parses the command line inputs and returns the resulting namespace"""

    parser = argparse.ArgumentParser(prog='abaci',
                description='Utility for compiling and running abaqus jobs with user subroutines', 
                epilog="""Run a subcommand with --help to view specific help for that command,
                           for example: abaci compile --help""")

    # Top-level options (all subcommands)

    parser.add_argument('-V','--version',help='show abaci version',
                        action='version', version="%(prog)s v0.2.0")

    verbose_group = parser.add_mutually_exclusive_group()

    verbose_group.add_argument('-v','--verbose',help='output more information from abaci',
                        dest='verbose',action='count',default=0)
    
    verbose_group.add_argument('-q','--quiet',help='output less information from abaci',
                        dest='verbose',action='store_const',const=-1)

    parser.add_argument('--config',type=str,help='specify a different config file to default ("abaci.toml")',
                        dest='config',default='abaci.toml')

    subparsers = parser.add_subparsers(help='Subcommand to run', dest='action')


    # Build command group
    build_group = argparse.ArgumentParser(add_help=False)

    build_group.add_argument('-t','--codecov',help='compile subroutines for code coverage analysis',
                        dest='codecov',action='store_true')

    build_group.add_argument('-d','--debug',help='compile with debug flags',
                        dest='debug',action='store_true')

    build_group.add_argument('-0','--noopt',help='compile without any optimisations',
                        dest='noopt',action='store_true')

    # RUN subcommand
    run_command = subparsers.add_parser('run', parents=[build_group],
                                         help='Compile user subroutines and run an abaqus job',
                                         description="Compile user subroutines and run one or abaqus jobs as described by job-spec")

    run_command.add_argument(metavar='job-spec',dest='job_spec',type=str,nargs='?',default='default',
                          help='Either: a comma-separated list of job tags or jobs names to filter jobs'
                                ' specified in the manifest; OR a path to an abaqus job file to run.')

    run_command.add_argument('-b','--background',help='run abaci in the background after compilation',
                        dest='background',action='store_true')

    run_command.add_argument('-n','--nproc',type=int,help='specify number of threads/processes to run with Abaqus',
                        dest='nproc',default=1)

    run_command.add_argument('-j','--jobs',type=int,help='run jobs concurrently, optionally specify a maximum number of concurrently running jobs',
                        nargs='?',dest='njob',action='store',const=None,default=1)

    
    # COMPILE subcommand
    compile_command = subparsers.add_parser('compile', parents=[build_group],
                                         help='Compile user subroutines only',
                                         description="Compile user subroutines and exit")

    # SHOW subcommand
    show_command = subparsers.add_parser('show', help='Show useful information about this project')

    show_command.add_argument(metavar='object',dest='object',type=str,nargs='*',default='jobs',
                             choices=['jobs','dependencies','config','sources'],
                             help='Query specific objects for information')

    args = parser.parse_args()

    args.verbose = min(args.verbose,2)
    
    if args.action == 'run':

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
