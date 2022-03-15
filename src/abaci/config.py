import os
import logging
import glob
from os.path import exists, relpath

from redist import toml
from redist.schema import Schema, And, Optional, Use, Or#

def load_config(args):
    """Top-level routine to read, parse, validate and sanitize config file"""

    config_file, config_dir = get_config_path(args)

    config_str = read_config_file(config_file)

    config = parse_config(config_str)

    config = sanitize_config(config, config_dir)

    if args.echo:
        print toml.dumps(config)
        exit()

    check_config(config)

    return config


def get_config_path(args):
    """Establish absolute path for config file"""

    log = logging.getLogger('abaci')

    config_file = os.path.realpath(args.config)
    config_dir = os.path.dirname(config_file)

    log.info('Config file is "%s"',relpath(config_file))
    log.debug('Config directory is "%s"',config_dir)

    return config_file, config_dir


def read_config_file(config_file):
    """Open the config file and read contents into a string"""

    with open(config_file, "r") as f:
        config_lines = f.readlines()

    config_str = "".join(config_lines)

    return config_str


def config_schema():
    """Defines the schema for the abaci.toml config files"""
    
    check_schema = Schema({'fields': [unicode],
                           'reference': unicode,
                           'steps': [unicode],
                           Optional('frames', default='last'): Or(u'all',u'last',[int]),
                           Optional('elements',default='all'): Or(u'all',[int])})

    job_schema = Schema([{'job-file': unicode,
                         Optional('include',default=[]): Or(unicode,[unicode]), 
                         Optional('tags',default=[]): Or(unicode,[unicode]),
                         Optional('name',default=None): unicode,
                         Optional('mp-mode',default='threads'): Or(u'threads',u'mpi',u'disable'),
                         Optional('check',default=None): check_schema}])

    compile_schema = Schema({Optional('fflags',default=[]): Or(unicode,[unicode]),
                            Optional('lflags',default=''): unicode,
                            Optional('opt-host',default=True): bool,
                            Optional('debug-symbols',default=False): bool,
                            Optional('runtime-checks',default=False): bool,
                            Optional('compiletime-checks',default=False): bool,
                            Optional('code-coverage',default=False): bool,
                            Optional('include',default=[]): Or(unicode,[unicode])})

    compile_defaults = compile_schema.validate({})

    config_schema = Schema(And(Use(toml.loads),{
                            Optional('output', default=u'.'): unicode,
                            'user-sub-file': unicode,
                            Optional('job',default=[]): job_schema,
                            Optional('compile',default=compile_defaults): And(dict,compile_schema)}))

    return config_schema


def parse_config(config_str):
    """Parse config toml and validate against the schema"""

    log = logging.getLogger('abaci')

    schema = config_schema()

    log.debug('Parsing config contents...')

    config = schema.validate(config_str)

    return config


def sanitize_config(config, config_dir):
    """Normalise paths in config"""
    
    log = logging.getLogger('abaci')
    
    log.debug('Santizing config contents...')

    # Optional lists
    if not isinstance(config['compile']['fflags'],list):
        config['compile']['fflags'] = [config['compile']['fflags']]
    
    if not isinstance(config['compile']['lflags'],list):
        config['compile']['lflags'] = [config['compile']['lflags']]

    if not isinstance(config['compile']['include'],list):
        config['compile']['include'] = [config['compile']['include']]

    # Output is relative to cwd
    config['output'] = os.path.realpath(config['output'])

    # User subroutine path is relative to the config file
    config['user-sub-file'] = os.path.realpath(os.path.join(
                                config_dir,config['user-sub-file']))

    # User subroutine include paths are relative to the config file
    #  and expand globbing
    compile_includes = []
    for ifile in config['compile']['include']:

        full_path = os.path.realpath(os.path.join(
                                config_dir,ifile))

        compile_includes.extend(glob.glob(full_path))

    config['compile']['include'] = compile_includes

    for j in config['job']:
        j['job-file'] = os.path.realpath(os.path.join(
                                config_dir,j['job-file']))

        if not isinstance(j['include'],list):
            j['include'] = [j['include']]

        for i,ifile in enumerate(j['include']):
            j['include'][i] = os.path.realpath(os.path.join(
                                config_dir,ifile))

        if not isinstance(j['tags'],list):
            j['tags'] = [j['tags']]

        if j['check']:
            j['check']['reference'] = os.path.realpath(os.path.join(
                                config_dir,j['check']['reference']))

    return config

def check_config(config):
    """Check config to raise any errors before continuing"""

    if not exists(config['user-sub-file']):
        raise Exception('The user subroutine file "{file}" cannot be found'.format(file=config['user-sub-file']))


def list_config_jobs(config,verbose):

    for i,j in enumerate(config['job']):

        if j['name']:

            job_name = j['name']

        else:

            job_name = os.path.basename(j['job-file'])

        print "    {i}: {name}  [{tags}]".format(
               i=i, name=job_name, tags=', '.join(j['tags']),
               file=os.path.relpath(j['job-file'],os.getcwd())
        )

        if verbose > 0:
             print "     ({file})".format(
               file=os.path.relpath(j['job-file'],os.getcwd())
        )