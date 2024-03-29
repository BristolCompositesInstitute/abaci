import logging
import os
import abaqus as abq
from utils import cwd, mkdir, copyfile, copydir, system_cmd, system_cmd_wait, relpathshort, to_ascii, hashfiles
from shutil import rmtree
from getpass import getuser
from hashlib import sha1
import json
import cPickle as pkl
import glob
import itertools

fortran_suffixes = ('.f','.f90','.for','.F90')

def compile_user_subroutine(args, output_dir, user_file, compile_conf, dep_list):
    """Perform pre-compilation step using abaqus make"""

    log = logging.getLogger('abaci')

    compile_dir = os.path.join(output_dir,'lib')

    compile_file = os.path.join(compile_dir,
                                 os.path.basename(user_file))

    includes = compile_conf['include'][:]

    aux_sources = compile_conf['sources']

    fflags = get_flags(compile_dir=compile_dir,
                      fortran_flags = compile_conf['fflags'],
                      debug_symbols = args.debug,
                      runtime_checks = args.debug,
                      compiletime_checks = args.check or compile_conf['compiletime-checks'],
                      codecov = args.codecov,
                      opt_host = compile_conf['opt-host'],
                      noopt = args.noopt)
    
    if not need_recompile(user_file,includes,aux_sources,dep_list,compile_conf,args,output_dir,compile_dir):
        log.info('Skipping compilation (source files unchanged)')
        return 0, compile_dir, fflags

    aux_source_list = stage_files(compile_dir, user_file, compile_file, includes, aux_sources, dep_list)

    compile_auxillary_sources(compile_dir,compile_conf,args,aux_source_list,fflags)

    log.debug('Flags = %s',fflags)

    if os.name == 'nt':
        lflags = compile_conf['lflags']['windows']
    else:
        lflags = compile_conf['lflags']['linux']

    spool_env_file(compile_dir,fflags,lflags)

    log.info('Running abaqus make')

    stat = abq.make(dir=compile_dir, lib_file=compile_file, verbosity=(args.verbose + 2*args.screen_output))
    
    return stat, compile_dir, fflags


def need_recompile(compile_file,includes,aux_sources,dep_list,compile_conf,args,output_dir,compile_dir):
    """Check if we can skip recompilation because nothing has changed"""

    log = logging.getLogger('abaci')

    dep_includes = list(itertools.chain.from_iterable(dep['includes'] for n,dep in dep_list.items()))
    dep_sources = list(itertools.chain.from_iterable(dep['sources'] for n,dep in dep_list.items()))

    files = [compile_file]+includes+aux_sources+dep_includes+dep_sources

    # Check for existing lib files
    if os.name == 'nt':
        ext = '.dll'
    else:
        ext = '.so'
    libfiles = glob.glob(os.path.join(compile_dir,'*'+ext))

    # Need to recompile if there are no library files
    if not libfiles:
        return True

    # Read previous compilation hash
    digest_cache = os.path.join(output_dir,'digest.pkl')
    if not os.path.isfile(digest_cache):
        old_digest = '0'
        
    else:
        with open(digest_cache,'r') as f:
            old_digest = pkl.load(f)

    compile_args = [args.check, args.debug, args.gcc, args.noopt, args.codecov]

    # Calculate new compilation hash
    src_digest = hashfiles(files)
    m = sha1()
    m.update(json.dumps(compile_conf,sort_keys=True))
    m.update(json.dumps(compile_args,sort_keys=True))
    m.update(src_digest)
    digest = m.hexdigest()

    # Cache new compilation hash
    with open(digest_cache,'w') as f:
        pkl.dump(digest,f)

    log.debug('Compilation digest: %s',digest)
    log.debug('Previous digest: %s',old_digest)

    # Recompile if hashes don't match
    return old_digest != digest


def get_mod_dir(compile_dir):
    """Define directory for storing module files"""

    return os.path.join(compile_dir,'mod')


def stage_files(compile_dir, user_file, compile_file, include_files, aux_sources, dep_list):
    """Create output compilation directory and move files there"""

    log = logging.getLogger('abaci')

    if os.path.exists(compile_dir):
        log.debug('Removing existing compile directory (%s)',relpathshort(compile_dir))
        rmtree(compile_dir)

    mkdir(compile_dir)

    mkdir(get_mod_dir(compile_dir))

    copyfile(user_file,compile_file)

    # Stage additional 'include' files from this project
    for inc in include_files:

        dest = os.path.join(compile_dir,os.path.basename(inc))

        if os.path.isdir(inc):

            copydir(inc,dest)

        else:

            copyfile(inc,dest)
    
    # Stage auxillary source files
    aux_source_list = []
    for src in aux_sources:

        dest = os.path.join(compile_dir,os.path.basename(src))

        aux_source_list.append(dest)

        if os.path.isdir(src):

            copydir(src,dest)

        else:

            copyfile(src,dest)

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

        for src in dep['sources']:

            dest = os.path.join(dep_dir,os.path.basename(src))
            
            aux_source_list.append(dest)

            if os.path.isdir(src):

                copydir(src,dest)

            else:

                copyfile(src,dest)

    return aux_source_list


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
    
    if os.name == 'nt':
        flags = fortran_flags['windows'][:]
    else:
        flags = fortran_flags['linux'][:]

    set_flag(flags,unix='-qopt-report-file={dir}/optrpt'.format(dir=compile_dir),
                    win='/Qopt-report-file:{dir}\optrpt'.format(dir=compile_dir))

    set_flag(flags,unix=['-module', get_mod_dir(compile_dir)],
                    win='/module:{dir}'.format(dir=get_mod_dir(compile_dir)))

    set_flag(flags,unix=['-error-limit','5'],
                    win='/error-limit:5')

    set_flag(flags,unix='-qopenmp',
                    win='/Qopenmp')

    set_flag(flags,unix=['-gen-interfaces','-warn','interfaces'],
                   win=['/gen-interfaces','/warn:interfaces'])

    if debug_symbols:
        set_flag(flags,unix=['-g','-debug'],win=['/debug','/Z7'])

    if runtime_checks:
        set_flag(flags,unix=['-check', 'all'],
                       win=['/check:all'])

    if compiletime_checks:
        set_flag(flags,unix=['-warn', 'all'],win='/warn:all')
    else:
        set_flag(flags,unix=['-check','noarg_temp_created'],win='/check:noarg_temp_created')

    if codecov:
        set_flag(flags,unix='-prof-gen=srcpos',win='/Qcov-gen')
        set_flag(flags,unix='-prof-dir={dir}'.format(dir=compile_dir),
                        win=['/Qcov-dir',compile_dir])

    if opt_host and not noopt:
        set_flag(flags,unix='-xHOST',win='/QxHOST')

    if noopt:
        set_flag(flags,unix='-O0',win='/Od')

    return flags



def get_cflags(use_gcc, c_flags, debug_symbols, compiletime_checks,
               opt_host, noopt):
    """Set platform specific flags for c compilation"""

    def set_flag(flags,intel_unix,intel_win,gnu):
        """Helper to add flag depending on platform"""
        
        import os
        
        if not isinstance(intel_unix,list):
            intel_unix = [intel_unix]

        if not isinstance(intel_win,list):
            intel_win = [intel_win]

        if not isinstance(gnu,list):
            gnu = [gnu]

        if use_gcc:

            flags.extend(gnu)

        else:

            if os.name == 'nt':
                flags.extend(intel_win)
            else:
                flags.extend(intel_unix)
    
    if use_gcc:
        flags = c_flags['gcc'][:]
    elif os.name == 'nt':
        flags = c_flags['windows'][:]
    else:
        flags = c_flags['linux'][:]

    set_flag(flags,intel_unix=['-diag-error-limit=5'],
                    intel_win=[],
                    gnu=["-fmax-errors=5"])

    if debug_symbols:
        set_flag(flags,intel_unix=['-g','-debug'],
                       intel_win=['/Z7'],
                       gnu="-g")

    if compiletime_checks:
        set_flag(flags,intel_unix=['-warn', 'all'],
                       intel_win='/Wall',
                       gnu=['-Wall', '-Wextra'])

    if opt_host and not noopt:
        set_flag(flags,intel_unix='-xHOST',
                       intel_win=[],
                       gnu="-march=native")

    if noopt:
        set_flag(flags,intel_unix='-O0',intel_win='/Od',gnu='-O0')
    else:
        set_flag(flags,intel_unix=[],intel_win='/O2',gnu="-O3")

    return flags


def compile_cpp(use_gcc, cflags, source_file, verbose):
    """Heler for compiling c/c++ source files"""

    log = logging.getLogger('abaci')

    base = os.path.basename(source_file)
    log.debug('Compiling auxillary source file "%s"',base)

    if use_gcc:
        if source_file.endswith('.cpp'):
            cc = 'g++'
        else:
            cc = 'gcc'
            
    elif os.name == 'nt':
        cc = 'cl'
    else:
        cc = 'icc'
        
    cmd = [cc,'-c',os.path.relpath(source_file)]
    cmd.extend(cflags)

    obj_file = base.split('.')[0] +'-std.o'

    if os.name == 'nt':
        obj_file += 'bj'

    if cc == 'cl':

        cmd.extend(["/Fo:",obj_file])

    else:

        cmd.extend(["-o",obj_file])

    p, ofile, efile = system_cmd(cmd,output=obj_file+'.log')

    stat = system_cmd_wait(p,verbose,ofile,efile)

    if stat != 0:

        log.fatal('(!) Error while compiling auxillary source "%s"',base)

        raise Exception('(!) Error while compiling auxillary source file')

    copyfile(obj_file,obj_file.replace('-std','-xpl'))
    copyfile(obj_file,obj_file.replace('-std','-xplD'))


def compile_fortran(use_gcc, fflags, source_file, verbose):
    """Heler for compiling auxiliary fortran source files"""

    log = logging.getLogger('abaci')

    base = os.path.basename(source_file)
    log.debug('Compiling auxillary source file "%s"',base)

    if use_gcc:
        fc = 'gfortran'
    else:
        fc = 'ifort'
        
    cmd = [fc,'-c',os.path.relpath(source_file)]
    cmd.extend(fflags)

    obj_file = base.split('.')[0] +'-std.o'

    if os.name == 'nt':
        obj_file += 'bj'

    if os.name == 'nt':

        cmd.extend(["/Fo"+obj_file])

    else:

        cmd.extend(["-o",obj_file])

    p, ofile, efile = system_cmd(cmd,output=obj_file+'.log')

    stat = system_cmd_wait(p,verbose,ofile,efile)

    if stat != 0:

        log.fatal('(!) Error while compiling auxillary source "%s"',base)

        raise Exception('(!) Error while compiling auxillary source file')

    copyfile(obj_file,obj_file.replace('-std','-xpl'))
    copyfile(obj_file,obj_file.replace('-std','-xplD'))



def compile_auxillary_sources(compile_dir,compile_conf,args,aux_source_list,fflags):
    """Perform separate compilation of auxillary sources files"""
    
    if not aux_source_list:

        return
    
    cflags = get_cflags(use_gcc=args.gcc,
                      c_flags = compile_conf['cflags'],
                      debug_symbols = args.debug,
                      compiletime_checks = args.check or compile_conf['compiletime-checks'],
                      opt_host = compile_conf['opt-host'],
                      noopt = args.noopt) 

    log = logging.getLogger('abaci')

    log.info('Compiling auxillary sources')

    with cwd(compile_dir):

        for src in aux_source_list:

            if src.endswith('.c') or src.endswith('.cpp'):
                
                compile_cpp(args.gcc, cflags, src, args.verbose + 2*args.screen_output)

            elif src.endswith(fortran_suffixes):

                compile_fortran(args.gcc, fflags, src, args.verbose + 2*args.screen_output)


def spool_env_file(compile_dir,fflags,lflags):
    """Generate the abaqus_v6.env file containing compiler flags"""

    env_file = os.path.join(compile_dir,'abaqus_v6.env')

    fflags = map(to_ascii,fflags)
    lflags = map(to_ascii,lflags)

    with open(env_file,'w') as f:

        f.write('compile_fortran.extend({fflags})\n'.format(fflags=fflags.__str__()))
        f.write('link_sl.extend({lflags})\n'.format(lflags=lflags.__str__()))

        f.write('print(" ".join(compile_fortran))\n')
        f.write('print(" ".join(link_sl))\n')


def prepare_release(compile_dir,release_dir):
    """Prepare a pre-compiled binary release directory for redistribution"""

    log = logging.getLogger('abaci')

    mkdir(release_dir)

    if os.name == 'nt':
        dest = os.path.join(release_dir,'win64')
    else:
        dest = os.path.join(release_dir,'linux64')

    if os.path.isdir(dest):
        log.fatal('(!) Release directory "%s" already exists, not overwriting.',dest)
        exit(1)
    
    mkdir(dest)

    if os.name == 'nt':
        log.info('Generating pre-compiled (Windows) binary release in "%s"',dest)
        log.info(' Rerun "abaci compile --release" on Linux to generate Linux binaries')
        ext = '.dll'
    else:
        log.info('Generating pre-compiled (Linux) binary release in "%s"',dest)
        log.info(' Rerun "abaci compile --release" on Windows to generate Windows binaries')
        ext = '.so'

    libfiles = glob.glob(os.path.join(compile_dir,'*'+ext))
    libfiles.extend(glob.glob(os.path.join(compile_dir,'abaqus-make.*')))

    for lib in libfiles:
        copyfile(lib,os.path.join(dest,os.path.basename(lib)))

    env_file = os.path.join(release_dir,'abaqus_v6.env')
    env_str = """## Abaqus environment file
##  (generated by Abaci compile --release)

import os

if os.name == 'nt':
    usub_lib_dir = os.path.join(os.getcwd(),r"win64")
else:
    usub_lib_dir = os.path.join(os.getcwd(),r"linux64")

del os
    """

    log.debug('Writing abaqus environment file in "%s"',env_file)
    with open(env_file,'w') as f:

        f.write(env_str)


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

