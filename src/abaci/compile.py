import logging
import os
from utils import cwd, mkdir, copyfile, copydir, system_cmd, system_cmd_wait, relpathshort
from shutil import rmtree
from getpass import getuser

def compile_user_subroutine(args, output_dir, user_file, compile_conf, dep_list):
    """Perform pre-compilation step using abaqus make"""

    log = logging.getLogger('abaci')

    compile_dir = os.path.join(output_dir,'lib')

    compile_file = os.path.join(compile_dir,
                                 os.path.basename(user_file))

    includes = compile_conf['include']

    stage_files(compile_dir, user_file, compile_file, includes, dep_list)

    flags = get_flags(compile_dir=compile_dir,
                      fortran_flags = compile_conf['fflags'],
                      debug_symbols = args.debug or compile_conf['debug-symbols'],
                      runtime_checks = args.debug or compile_conf['runtime-checks'],
                      compiletime_checks = compile_conf['compiletime-checks'],
                      codecov = args.codecov or compile_conf['code-coverage'],
                      opt_host = compile_conf['opt-host'],
                      noopt = args.noopt)

    log.debug('Flags = %s',flags)

    spool_env_file(compile_dir,flags)

    stat = run_abq_make(compile_file, compile_dir,args.verbose)
    
    return stat, compile_dir

def stage_files(compile_dir, user_file, compile_file, include_files, dep_list):
    """Create output compilation directory and move files there"""

    log = logging.getLogger('abaci')

    if os.path.exists(compile_dir):
        log.debug('Removing existing compile directory (%s)',relpathshort(compile_dir))
        rmtree(compile_dir)

    mkdir(compile_dir)

    copyfile(user_file,compile_file)

    # Stage additional 'include' files from this project
    for inc in include_files:

        dest = os.path.join(compile_dir,os.path.basename(inc))

        if os.path.isdir(inc):

            copydir(inc,dest)

        else:

            copyfile(inc,dest)
        
    # Stage 'include' files from dependencies
    #  (in subdirectories named by dependency name)
    for dep_name,dep in dep_list.items():

        dep_dir = os.path.join(compile_dir,dep_name)

        mkdir(dep_dir)
        
        for inc in dep['includes']:

            dest = os.path.join(dep_dir,os.path.basename(inc))

            if os.path.isdir(inc):

                copydir(inc,dest)

            else:

                copyfile(inc,dest)


def get_flags(compile_dir,fortran_flags, debug_symbols, runtime_checks, compiletime_checks, codecov,
               opt_host, noopt):
    """Set platform specific flags based on attributes"""

    def set_flag(flags,unix,win):
        """Helper to add flag depending on platform"""
        
        import os
        
        if not isinstance(unix,list):
            unix = [unix]

        if not isinstance(win,list):
            win = [win]

        if os.name == 'nt':
            flags.extend(win)
        else:
            flags.extend(unix)
    

    flags = fortran_flags

    set_flag(flags,unix='-qopt-report-file={dir}/optrpt'.format(dir=compile_dir),
                    win='/Qopt-report-file:{dir}\optrpt'.format(dir=compile_dir))

    if debug_symbols:
        set_flag(flags,unix=['-g','-debug'],win=['/debug','/Z7'])

    if runtime_checks:
        set_flag(flags,unix=['-check', 'all'],win='/check:all')

    if compiletime_checks:
        set_flag(flags,unix=['-warn', 'all'],win='/warn:all')

    if codecov:
        set_flag(flags,unix='-prof-gen=srcpos',win='/Qcov-gen')
        set_flag(flags,unix='-prof-dir={dir}'.format(dir=compile_dir),
                        win=['/Qcov-dir',compile_dir])

    if opt_host and not noopt:
        set_flag(flags,unix='-xHOST',win='/QxHOST')

    if noopt:
        set_flag(flags,unix='-O0',win='/Od')

    return flags


def spool_env_file(compile_dir,flags):
    """Generate the abaqus_v6.env file containing compiler flags"""

    env_file = os.path.join(compile_dir,'abaqus_v6.env')

    with open(env_file,'w') as f:

        f.write('compile_fortran.extend({flags})\n'.format(flags=flags.__str__()))


def run_abq_make(compile_file, compile_dir, verbosity):
    """Invoke abaqus make"""

    log = logging.getLogger('abaci')

    abqmake_cmd = ['abaqus','make','library={file}'.format(file=os.path.basename(compile_file))]

    if os.name == 'nt':
        abqmake_cmd[0] = 'c:\\SIMULIA\\Commands\\abaqus.bat'
        abqmake_cmd.append('&')
        abqmake_cmd.append('exit')
		
    log.info('Running abaqus make')

    with cwd(compile_dir):

        p,ofile,efile = system_cmd(abqmake_cmd, output=os.path.join(compile_dir,'abaqus-make'))

        stat = system_cmd_wait(p,verbosity,ofile,efile)

    return stat


def collect_cov_report(config,compile_dir,verbosity):
    """Run profmerge to get coverage report"""

    # Need to restage original compilation source file

    user_file = config['user-sub-file']

    abq_temp = "/tmp/{user}_abaqus_make".format(user=getuser())

    mkdir(abq_temp)

    dest = os.path.join(abq_temp,os.path.basename(user_file))
    
    copyfile(user_file,dest)

    with cwd(compile_dir):

        system_cmd(['profmerge'],verbosity)
        system_cmd(['codecov','-prj','abaci','-spi','pgopti.spi'],verbosity)

        system_cmd(['codecov','-prj','abaci','-spi','pgopti.spi','-txtbcvrg','coverage.txt'],verbosity)

