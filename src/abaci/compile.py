import logging
import os
from utils import cwd, mkdir, copyfile
import subprocess
from shutil import rmtree

def compile_user_subroutine(args,config):
    """Perform pre-compilation step using abaqus make"""

    log = logging.getLogger('abaci')

    output_dir = config['output']

    compile_dir = os.path.join(output_dir,'lib')

    user_file = config['user-sub-file']

    compile_file = os.path.join(compile_dir,
                                 os.path.basename(user_file))

    compile_conf = config['compile']

    includes = compile_conf['include']

    stage_files(compile_dir, user_file, compile_file, includes)

    flags = get_flags(compile_dir=compile_dir,
                      fortran_flags = compile_conf['fflags'],
                      debug_symbols = args.debug or compile_conf['debug-symbols'],
                      runtime_checks = args.debug or compile_conf['runtime-checks'],
                      compiletime_checks = compile_conf['compiletime-checks'],
                      codecov = args.codecov or compile_conf['code-coverage'])

    log.debug('Flags = %s',flags)

    spool_env_file(compile_dir,flags)

    run_abq_make(compile_file, compile_dir)
    
    return compile_dir

def stage_files(compile_dir, user_file, compile_file, include_files):
    """Create output compilation directory and move files there"""

    log = logging.getLogger('abaci')

    if os.path.exists(compile_dir):
        log.info('Removing existing compile directory (%s)',compile_dir)
        rmtree(compile_dir)

    mkdir(compile_dir)

    copyfile(user_file,compile_file)

    for inc in include_files:
        dest = os.path.join(compile_dir,os.path.basename(inc))
        copyfile(inc,dest)


def get_flags(compile_dir,fortran_flags, debug_symbols, runtime_checks, compiletime_checks, codecov):
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
        set_flag(flags,unix='-g',win=['/debug','/Z7'])

    if runtime_checks:
        set_flag(flags,unix=['-check', 'all'],win='/check:all')

    if compiletime_checks:
        set_flag(flags,unix=['-warn', 'all'],win='/warn:all')

    if codecov:
        set_flag(flags,unix='-prof-gen=srcpos',win='/Qcov-gen')
        set_flag(flags,unix='-prof-dir={dir}'.format(dir=self.compile_dir),
                        win=['/Qcov-dir',self.compile_dir])

    return flags


def spool_env_file(compile_dir,flags):
    """Generate the abaqus_v6.env file containing compiler flags"""

    env_file = os.path.join(compile_dir,'abaqus_v6.env')

    with open(env_file,'w') as f:

        f.write('compile_fortran.extend({flags})\n'.format(flags=flags.__str__()))


def run_abq_make(compile_file, compile_dir):
    """Invoke abaqus make"""

    log = logging.getLogger('abaci')

    abqmake_cmd = ['abaqus','make','library={file}'.format(file=os.path.basename(compile_file))]

    if os.name == 'nt':
        abqmake_cmd[0] = 'c:\\SIMULIA\\Commands\\abaqus.bat'
    
    log.info('Running abaqus make')

    with cwd(compile_dir):

        log.debug('Running command "%s"',' '.join(abqmake_cmd))

        try:
            p = subprocess.Popen(abqmake_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

            for line in p.stdout:
                print(line)

            for line in p.stderr:
                print(line)

        except KeyboardInterrupt:
            p.kill()