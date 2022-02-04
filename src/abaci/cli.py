import argparse
import logging

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

    parser.add_argument('-b','--background',help='run abaci in the background after compilation and write output to log file (default abaci.log)',
                        dest='background',action='store_true')

    parser.add_argument('--log',type=str,help='specify log file to which to redirect abaci output',
                        dest='logfile',default=None)

    parser.add_argument('--config',type=str,help='specify a different config file to default ("abaci.toml")',
                        dest='config',default='abaci.toml')

    parser.add_argument('-j','--jobs',type=int,help='specify number of mpi jobs to run with Abaqus',
                        dest='jobs',default=1)

    return parser



def parse_cli():
    """Parses the command line inputs and returns the resulting namespace"""

    parser = abaci_cli()

    args = parser.parse_args()

    if args.show_version:
        print('Abaci version 0.1.0 (alpha)')
        exit()

    args.verbose = min(args.verbose,2)

    # No screen output if going into the background
    if args.background:
        args.verbose = -1

    # Normalise the job-spec into a list
    if ',' in args.job_spec:
        args.job_spec = args.job_spec.split(',')
    else:
        args.job_spec = [args.job_spec]

    return args


def init_logger(args):
    """Initialise the abaci global logger"""

    log_fmt = '%(levelname)8s: %(message)s'

    # Log to file if specified or if going into the background
    if args.background or args.logfile:
        logging.basicConfig(format=log_fmt,filename=(args.logfile or 'abaci.log'),level=logging.DEBUG)

    else:
        logging.basicConfig(format=log_fmt, level = 10*(2-args.verbose))

    log = logging.getLogger('abaci')
    
    log.debug('cli args=%s',args)

    log.debug('Verbosity is %s',args.verbose)