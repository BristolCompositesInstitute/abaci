from redist import toml
import os
from abaci.utils import recurse_files, relpathshort
from abaci.tests import discover_tests
from redist.tabulate import tabulate
from textwrap import wrap

def show_info(args, config, dep_list):
    """Show useful information about the current project"""
         
    if 'config' in args.object:

        print(toml.dumps(config))

    if 'jobs' in args.object:

        show_config_jobs(config,args.verbose)

    if 'dependencies' in args.object:

        show_dependencies(dep_list)

    if 'sources' in args.object:

        show_sources(config,dep_list)

    if 'tests' in args.object:

        show_tests(config['test-mod-dir'])


def show_dependencies(dep_list):
    """Print dependency list"""

    if not dep_list:

        return

    table = []

    for dep_name,dep in dep_list.items():

        table.append([dep_name,dep['version'],dep['git']])

    print(tabulate(table,tablefmt="plain",colalign=("right",)))


def show_sources(config,dep_list):
    """ List source files from this project and its dependencies
    
        List file names in the way that they would be 'included'
        into a top-level Fortran user subroutine.
    """

    sources = [' [user-sub] '+os.path.basename(config['user-sub-file'])]
    
    # Include files from this project
    for inc in config['compile']['include']:

        for file in recurse_files(inc):

            file_rel = os.path.relpath(file,os.path.dirname(inc))
            
            sources.append(' [included] '+file_rel)

    # Aux source files from this project
    for src in config['compile']['sources']:

        for file in recurse_files(src):

            file_rel = os.path.relpath(file,os.path.dirname(src))
            
            sources.append(' [compiled] '+file_rel)

    # Include files from dependencies
    #  (deployed in a subfolder named after the dependency)
    for dep_name,dep in dep_list.items():

        for inc in dep['includes']:

            for file in recurse_files(inc):

                file_rel = os.path.relpath(file,os.path.dirname(inc))
                
                sources.append(' [included] '+os.path.join(dep_name,file_rel))

    # Aux source files from dependencies
    #  (deployed in a subfolder named after the dependency)
    for dep_name,dep in dep_list.items():

        for src in dep['sources']:

            for file in recurse_files(src):

                file_rel = os.path.relpath(file,os.path.dirname(src))
                
                sources.append(' [compiled] '+os.path.join(dep_name,file_rel))

    for file in sources:

        print(os.path.relpath(file))


def show_config_jobs(config,verbose):
    """Print list of jobs in config file"""

    if not config['job']:

        return

    table = []

    for i,j in enumerate(config['job']):

        if j['name']:

            job_name = j['name']

        else:

            job_name = os.path.basename(j['job-file'])
        
        tags=','.join(j['tags'])

        file_path = '\n'.join(wrap(relpathshort(j['job-file']),70))

        table.append([job_name,tags])

        if verbose > 0:
            table.append([None,file_path])

    print(tabulate(table,tablefmt="plain",colalign=("right",)))


def show_tests(test_dir):
    """Print a list of test modules and test subroutines"""

    print ' Looking for tests in "{d}"'.format(d=test_dir)
    
    test_sources, testsuites = discover_tests(test_dir)
    
    for suite in testsuites:

        print '  module {s}'.format(s=suite["name"])
        if not suite["tests"]:
            
            print '    No test subroutines found'
        
        else:
            
            for test in suite['tests']:

                print '    subroutine {t}()'.format(t=test)

        
    