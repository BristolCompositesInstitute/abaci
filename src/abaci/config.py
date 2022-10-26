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
                         Optional('abq-flags',default=[]): Or(unicode,[unicode]),
                         Optional('post-process',default=[]): Or(unicode,[unicode]),
                         Optional('check',default=None): check_schema,
                         Optional('cluster',default=None): job_cluster_schema}])

    dependency_schema = Schema([{'name': unicode,
                                'git': unicode,
                                'version': unicode}])

    flag_schema = Schema({Optional('linux',default=[]): Or(unicode,[unicode]),
                          Optional('windows',default=[]): Or(unicode,[unicode]),
                          Optional('gcc',default=[]): Or(unicode,[unicode])})

    flag_schema_defaults = flag_schema.validate({})

    compile_schema = Schema({Optional('fflags',default=flag_schema_defaults): flag_schema,
                            Optional('cflags',default=flag_schema_defaults): flag_schema,
                            Optional('lflags',default=flag_schema_defaults): flag_schema,
                            Optional('opt-host',default=False): bool,
                            Optional('compiletime-checks',default=False): bool,
                            Optional('sources',default=[]): Or(unicode,[unicode]),
                            Optional('include',default=[]): Or(unicode,[unicode])})

    compile_defaults = compile_schema.validate({})

    config_schema = Schema(And(Use(toml.loads),{
                            Optional('name', default=None): unicode,
                            Optional('output', default=u'scratch'): unicode,
                            Optional('user-sub-file',default=None): unicode,
                            Optional('test-mod-dir',default='test'): unicode,
                            Optional('abq-flags',default=[]): Or(unicode,[unicode]),
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

    def ensure_list(potential_list):
        """Helper to unify optional list inputs"""
        if not isinstance(potential_list,list):

            return [potential_list]

        else:

            return potential_list

    # Optional lists

    config['abq-flags'] = ensure_list(config['abq-flags'])

    for flag_group in ('fflags','cflags','lflags'):

        for flag_target in ('linux','windows','gcc'):

            config['compile'][flag_group][flag_target] = ensure_list(config['compile'][flag_group][flag_target])
    
    for field in ('include','sources'):

        config['compile'][field] = ensure_list(config['compile'][field])

    # Output is relative to cwd
    config['output'] = os.path.realpath(config['output'])

    # User subroutine path is relative to the config file
    if config['user-sub-file']:
        config['user-sub-file'] = os.path.realpath(os.path.join(
                                config_dir,config['user-sub-file']))

    config['test-mod-dir'] = os.path.realpath(os.path.join(
                                config_dir,config['test-mod-dir']))

    # Automatically include *.f and *.f90 from user-sub directory
    if config['user-sub-file']:
        usub_dir = os.path.dirname(config['user-sub-file'])
        for ext in ['.f', '.for', '.f90']:
            auto_include = os.path.join(usub_dir,'*'+ext)
            config['compile']['include'].extend(glob.glob(auto_include))
        config['compile']['include'].remove(config['user-sub-file'])

    # User subroutine include paths are relative to the config file
    #  and expand globbing
    compile_includes = []
    for ifile in config['compile']['include']:

        full_path = os.path.realpath(os.path.join(
                                config_dir,ifile))

        compile_includes.extend(glob.glob(full_path))

    config['compile']['include'] = compile_includes

    # User subroutine auxillary source file paths are relative to the config file
    #  and expand globbing
    compile_sources = []
    for sfile in config['compile']['sources']:

        full_path = os.path.realpath(os.path.join(
                                config_dir,sfile))

        compile_sources.extend(glob.glob(full_path))

    config['compile']['sources'] = compile_sources

    for j in config['job']:
        j['job-file'] = os.path.realpath(os.path.join(
                                config_dir,j['job-file']))

        j['include'] = ensure_list(j['include'])

        extra_includes = []
        for i,ifile in enumerate(j['include']):
            j['include'][i] = os.path.realpath(os.path.join(
                                config_dir,ifile))

            extra_includes.extend(glob.glob(j['include'][i]))


        if j['job-file'] in extra_includes:
            extra_includes.remove(j['job-file'])

        j['include'] = extra_includes

        j['tags'] = ensure_list(j['tags'])

        j['abq-flags'] = ensure_list(j['abq-flags'])

        # Apply abq-flag defaults from top-level field if empty
        if not j['abq-flags']:

            j['abq-flags'] = config['abq-flags']

        if j['check']:
            j['check']['reference'] = os.path.realpath(os.path.join(
                                config_dir,j['check']['reference']))

        j['post-process'] = ensure_list(j['post-process'])

        # Substitute {ROOT} for config dir at this stage
        for i, script in enumerate(j['post-process']):

            j['post-process'][i] = script.replace(
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



def init_new_config(file_path,user_sub_file=None,output=None,full=None,bare=None,overwrite=None):
    """Initialise a new config file"""

    log = logging.getLogger('abaci')

    if exists(file_path):

        if not overwrite:

            log.fatal('(!) File "%s" already exists, not overwriting',file_path)

            exit(1)

        else:

            log.warn('Overwriting file %s with new configuration',file_path)


    user_sub_file = user_sub_file or "user.f"
    output = output or "scratch"

    config_str = """## Abaci configuration file
##
##  Lines beginning with '#' are comments
##  See the abaci documentation for a full definition of this file
##  Read more about the toml format here: https://toml.io/
##
##  File and folder paths are relative to the location
##   of this config file
##

## Path to your main user subroutine file
user-sub-file = "{usub}"

## Path for output directory
output = "{output}"

## Extra arguments to pass to Abaqus
abq-flags = ""
    """.format(usub=user_sub_file,output=output)

    if full:

        config_str +="""
## --- Compilation settings section ----
[compile]

## List of included files
include = []

## List of auxilliary C/C++ source files to compile
sources  = []

## Enable host-specific compiler optimisations
opt-host = false

## Enforce strict compile-time code checks
compiletime-checks = false

## Extra fortran compiler flags
fflags.linux = ""
fflags.windows = ""

## Extra C/C++ compiler flags
cflags.linux = ""
cflags.windows = ""

## Extra linker flags
lflags.linux = ""
lflags.windows = ""
        """

        schema, schema_defaults = get_default_cluster_schema()

        config_str += """
## --- HPC Cluster default settings ---
[cluster]
"""

        config_str += toml.dumps(schema_defaults)

    config_str += """       
## Uncomment lines below to define a job
# [[job]]
# name = "myjob"
# job-file = "job.inp"
# mp-mode = "threads"
# tags = ["default"]
# include = []         # extra files needed for this job
"""

    if bare:

        output = ''

        for line in config_str.split('\n'):

            if line[0:2] != '##' and len(line) > 0:

                output += line + '\n'
    else:

        output = config_str

    with open(file_path,'w') as f:

        f.write(output)
    


