import os
import logging
import glob
from os.path import exists

from redist import toml
from redist.schema import Schema, And, Optional, Use, Or#
from abaci.utils import relpathshort

def load_config(config_file,echo):
    """Top-level routine to read, parse, validate and sanitize config file"""

    log = logging.getLogger('abaci')
    
    config_file, config_dir = get_config_path(config_file)

    if not exists(config_file):

        log.fatal('Unable to find config file "%s"',config_file)

        exit(1)

    config_str = read_config_file(config_file)

    config = parse_config(config_str)

    config = sanitize_config(config, config_dir)

    check_config(config)

    return config, config_dir


def get_config_path(config_file):
    """Establish absolute path for config file"""

    log = logging.getLogger('abaci')

    config_file = os.path.realpath(config_file)
    config_dir = os.path.dirname(config_file)

    log.debug('Config file is "%s"',relpathshort(config_file))
    log.debug('Config directory is "%s"',config_dir)

    return config_file, config_dir


def read_config_file(config_file):
    """Open the config file and read contents into a string"""

    with open(config_file, "r") as f:
        config_lines = f.readlines()

    config_str = "".join(config_lines)

    return config_str


def get_default_cluster_schema():
    """Returns the default (top-level) cluster schema"""

    schema = Schema({Optional('time',default='01:00:00'): unicode,
                           Optional('partition',default=None): unicode,
                           Optional('nodes',default=1): int,
                           Optional('tasks-per-node',default=1): int,
                           Optional('cpus-per-task',default=1): int,
                           Optional('mem-per-cpu',default='4000m'): unicode,
                           Optional('email',default=None): unicode
                           })

    schema_defaults = schema.validate({})

    return schema, schema_defaults


def config_schema():
    """Defines the schema for the abaci.toml config files"""
    
    default_cluster_schema, cluster_defaults = get_default_cluster_schema()

    job_cluster_schema = Schema({Optional('time',default=None): unicode,
                           Optional('partition',default=None): unicode,
                           Optional('nodes',default=None): int,
                           Optional('tasks-per-node',default=None): int,
                           Optional('cpus-per-task',default=None): int,
                           Optional('mem-per-cpu',default=None): unicode,
                           Optional('email',default=None): unicode
                           })

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
                         Optional('post-process',default=None): unicode,
                         Optional('check',default=None): check_schema,
                         Optional('cluster',default=None): job_cluster_schema}])

    dependency_schema = Schema([{'name': unicode,
                                'git': unicode,
                                'version': unicode}])

    compile_schema = Schema({Optional('fflags',default=[]): Or(unicode,[unicode]),
                            Optional('opt-host',default=True): bool,
                            Optional('compiletime-checks',default=False): bool,
                            Optional('include',default=[]): Or(unicode,[unicode])})

    compile_defaults = compile_schema.validate({})

    config_schema = Schema(And(Use(toml.loads),{
                            Optional('name', default=None): unicode,
                            Optional('output', default=u'.'): unicode,
                            Optional('user-sub-file',default=None): unicode,
                            Optional('cluster',default=cluster_defaults): default_cluster_schema,
                            Optional('dependency',default=[]): dependency_schema,
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

    if not isinstance(config['compile']['include'],list):
        config['compile']['include'] = [config['compile']['include']]

    # Output is relative to cwd
    config['output'] = os.path.realpath(config['output'])

    # User subroutine path is relative to the config file
    if config['user-sub-file']:
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

        # Substitute {ROOT} for config dir at this stage
        if j['post-process']:

            j['post-process'] = j['post-process'].replace(
                            r'{ROOT}',config_dir)

        # Apply top-level cluster defaults to individual jobs
        if not j['cluster']:

            j['cluster'] = config['cluster']

        else:
            
            for field in j['cluster']:

                if not j['cluster'][field]:

                    j['cluster'][field] = config['cluster'][field]


    return config


def check_config(config):
    """Check config to raise any errors before continuing"""

    if config['user-sub-file'] and not exists(config['user-sub-file']):
        raise Exception('The user subroutine file "{file}" cannot be found'.format(file=config['user-sub-file']))


    for j in config['job']:

        if not exists(j['job-file']):

            raise Exception('The job file "{file}" cannot be found'.format(file=j['job-file']))