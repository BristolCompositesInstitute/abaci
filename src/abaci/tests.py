import logging
import glob
import os
from os import listdir
from os.path import isfile, join, realpath, dirname, pardir, relpath, basename

from abaci.fortran_parsing import parse_fortran_file
from abaci.compile import fortran_suffixes, compile_fortran
from abaci.utils import system_cmd, system_cmd_wait, copyfile, cwd

def discover_tests(test_dir):
    """Find Fortran files in test_dir and parse contents for test subroutines"""

    log = logging.getLogger('abaci')

    test_sources = [join(test_dir,f) for f in listdir(test_dir) 
                      if isfile(join(test_dir, f)) and f.endswith(fortran_suffixes)]

    log.debug('Fortran sources in test dir: %s', test_sources)

    srcs = []

    for srcfile in test_sources:

        srcs.append(parse_fortran_file(srcfile))

    testsuites = []

    for src in srcs:

        for mod in src:

            if mod.startswith('test'):

                testsuites.append({'name':mod, 'tests':[]})

                for sub in src[mod]['subroutines']:

                    if sub.startswith('test'):

                        testsuites[-1]['tests'].append(sub)

                if not testsuites[-1]['tests']:

                    del testsuites[-1]

                else:

                    log.debug("Testsuite '%s' : %s",mod,testsuites[-1]['tests'])

    if not testsuites:

        log.warn('(!) No tests found in directory "%s"',test_dir)

    return test_sources, testsuites


def stage_test_source_files(libdir, test_mod_sources):
    """Copy source files for tests to compile directory"""

    install_location = realpath(join(dirname(realpath(__file__)), pardir))

    test_framework = join(install_location,'fortran','naturalfruit.f90')

    test_sources = [test_framework]
    test_sources.extend(test_mod_sources)

    test_files = []
    for source in test_sources:

        dest = join(libdir,basename(source))
        test_files.append(dest)
        copyfile(source,dest)

    return test_files


def get_object_ext(libdir, usub_file):
    """Detect the correct object file extension for Abaqus standard/explicit/explicitDP"""
    
    usub_name = os.path.splitext(os.path.basename(usub_file))[0]

    if os.name == 'nt':
        obj = '.obj'
    else:
        obj = '.o'

    options = ['-std'+obj,'-xpl'+obj,'-xplD'+obj]

    # Detect extension based on output of 'Abaqus make'
    for ext in options:

        if os.path.exists(os.path.join(libdir,usub_name+ext)):
            return ext

    raise Exception('Unable to determine correct object extension (-std,-xpl,-xplD).')


def compile_tests(args, usub_file, fflags, libdir, test_driver_source, test_mod_sources):
    """Compile Fortran test modules and test driver"""

    log = logging.getLogger('abaci')

    log.info('Compiling tests')

    ext = get_object_ext(libdir, usub_file)

    link_objects = glob.glob(join(libdir,'*'+ext))

    test_files = stage_test_source_files(libdir, test_mod_sources)

    test_files.append(test_driver_source)
    if args.gcc:
        fc = 'gfortran'
    else:
        fc = 'ifort'
    
    out_file = 'test-driver'

    cmd = [fc]
    cmd.extend([relpath(o,libdir) for o in link_objects])
    cmd.extend([basename(f) for f in test_files])
    cmd.extend(fflags)
    
    if os.name == 'nt':

        out_file += '.exe'

        cmd.extend(["/Fe"+out_file])

        cmd.append('/iface:cref')

        cmd.extend(['/link'])
        cmd.extend('/NODEFAULTLIB:LIBC.LIB /NODEFAULTLIB:LIBCMT.LIB /DEFAULTLIB:OLDNAMES.LIB /DEFAULTLIB:LIBIFCOREMD.LIB /DEFAULTLIB:LIBIFPORTMD.LIB /DEFAULTLIB:LIBMMD.LIB /DEFAULTLIB:kernel32.lib /DEFAULTLIB:user32.lib /DEFAULTLIB:advapi32.lib'.split())
        cmd.extend('oldnames.lib user32.lib ws2_32.lib netapi32.lib advapi32.lib msvcrt.lib vcruntime.lib ucrt.lib'.split())
    
    else:

        cmd.extend(["-o",out_file])

        cmd.extend(['-shared-intel'])

    with cwd(libdir):

        p, ofile, efile = system_cmd(cmd,output=out_file+'.log')

        stat = system_cmd_wait(p,args.verbose,ofile,efile)

    if stat != 0:

        log.fatal('(!) Error while compiling tests')

        raise Exception('(!) Error while compiling tests')

    return join(libdir,out_file)



def run_tests(test_driver,libdir,verbose):
    """Execute the test driver"""

    log = logging.getLogger('abaci')

    log.info('Running tests')

    cmd = [test_driver]

    p, ofile, efile = system_cmd(cmd,output=join(libdir,'tests'+'.log'))

    stat = system_cmd_wait(p,2*verbose + 2,ofile,efile)

    if stat != 0:

        log.warning('(!) Non-zero status return by test driver (%s)',stat)

    return stat



def gen_test_driver(testsuites, libdir):
    """Generate the main test driver program (fortran)"""

    log = logging.getLogger('abaci')

    install_location = realpath(join(dirname(realpath(__file__)), pardir))

    driver_template = join(install_location,'fortran','test-driver.template.f90')

    log.debug('Using test driver template "%s"',driver_template)

    with open(driver_template,'r') as f:

        template = f.read()

    test_driver = template.format(TEST_ARRAY=serialise_tests(testsuites),
                                  USE_MODULES=serialise_modules(testsuites))

    test_driver_file = join(libdir,'test-driver.f90')

    log.debug('Writing test driver to "%s"',test_driver_file)

    with open(test_driver_file,'w') as f:
        
        f.write(test_driver)

    return test_driver_file
    

def serialise_modules(testsuites):
    """Get Fortran module use statements for all testsuites"""

    repr = ""

    for suite in testsuites:

        repr += 'use {mod}\n'.format(mod=suite['name'])

    return repr



def serialise_tests(testsuites):
    """Get the Fortran representation for test cases and test suites"""

    repr = "[ &\n"

    indent = " "*15

    for suite in testsuites:

        if not suite["tests"]:
            continue

        repr += indent + "  testsuite_t(name='{n}', tests=[ &\n".format(n=suite["name"])

        for test in suite["tests"]:

            repr += indent + "    test_t(name='{n}', test_sub={t}), &\n".format(n=test,t=test)

        repr = repr[0:-4] + " &\n"

        repr += indent + "  ]), &\n"

    repr = repr[0:-4] + " &\n"
    repr += indent + "]"

    return repr
    



