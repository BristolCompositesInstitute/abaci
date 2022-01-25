import logging
import os
from contextlib import contextmanager
import subprocess
from unicodedata import normalize

@contextmanager
def cwd(path):
    """Helper to change directory temporarily"""

    log = logging.getLogger('abaci')

    oldpwd=os.getcwd()

    log.debug('Changing into directory "%s"',path)
    os.chdir(path)

    try:
        yield
    finally:
        log.debug('Changing back to directory "%s"',oldpwd)
        os.chdir(oldpwd)


def mkdir(dir):
    """Make a directory, if it doesn't exist"""

    log = logging.getLogger('abaci')

    if os.path.isdir(dir):
        
        log.debug('Directory already exists ("%s")',dir)

    else:

        log.debug('Making directory "%s"',dir)
        os.mkdir(dir)

def copyfile(source,dest):
    """Helper to copyfile"""
    from shutil import copyfile

    log = logging.getLogger('abaci')
    
    log.debug('Copying "%s" to "%s"',source, dest)
    copyfile(source,dest)


def system_cmd(cmd,verbosity):
    """Helper to launch system commands"""

    log = logging.getLogger('abaci')

    log.debug('Running command "%s"',' '.join(cmd))

    try:
        p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        o,e = p.communicate()

        # Print outputs if (non-zero status and not in quiet mode) or
        #  if in very verbose mode
        if (p.returncode != 0 and verbosity > -1) or verbosity > 1:
            print o
            print e

        elif verbosity > 0:
            print e

        if p.returncode != 0:
            log.warn('Command exited with status %s (%s)',p.returncode,' '.join(cmd))

    except KeyboardInterrupt:
        p.kill()

    return p.returncode

def to_ascii(ustring):

    return normalize('NFKD',ustring).encode('ascii','ignore')
