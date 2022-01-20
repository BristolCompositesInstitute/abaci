import argparse
import logging

def abaci_cli():
    """Defines the command line interface parser"""

    parser = argparse.ArgumentParser(prog='abaci',
                description='Utility for compiling and running abaqus jobs with user subroutines',
                usage='abaci [job-spec] [optional arguments]')
    
    parser.add_argument(metavar='job-spec',dest='job_spec',type=str,nargs='?',default='default',
                          help='Either: a comma-separated list of job tags or jobs names to filter jobs'
                                ' specified in the manifest; OR a path to an abaqus job file to run.')

    parser.add_argument('-V','--version',help='show abaci version',
                        dest='show_version',action='store_true')

    verbose_group = parser.add_mutually_exclusive_group()

    verbose_group.add_argument('-v','--verbose',help='output more information from abaqi',
                        dest='verbose',action='count',default=0)
    
    verbose_group.add_argument('-q','--quiet',help='don\'t output anything from abaqi',
                        dest='verbose',action='store_const',const=-1)

    parser.add_argument('-e','--echo',help='parse and display the config file, then stop.',
                        dest='echo',action='store_true',default=False)

    parser.add_argument('-t','--codecov',help='compile subroutines for code coverage analysis',
                        dest='codecov',action='store_true')

    parser.add_argument('-d','--debug',help='compile with debug flags',
                        dest='debug',action='store_true')

    parser.add_argument('-c','--compile',help='compile only, don\'t run abaqus',
                        dest='compile',action='store_true')

    parser.add_argument('--config',type=str,help='specify a different config file to default ("abaci.toml")',
                        dest='config',default='abaci.toml')

    return parser



def parse_cli():
    """Parses the command line inputs and returns the resulting namespace"""

    parser = abaci_cli()

    args = parser.parse_args()

    if args.show_version:
        print('Abaci version 0.0.0')
        exit()

    args.verbose = min(args.verbose,2)

    # Normalise the job-spec into a list
    if ',' in args.job_spec:
        args.job_spec = args.job_spec.split(',')
    else:
        args.job_spec = [args.job_spec]

    return args


def init_logger(args):
    """Initialise the abaci global logger"""

    logging.basicConfig(format='%(levelname)8s: %(message)s')
    log = logging.getLogger('abaci')

    log.setLevel(10*(3-args.verbose))
    
    log.debug('cli args=%s',args)

    log.info('Verbosity is %s',args.verbose)