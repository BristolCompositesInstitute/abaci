import logging
import os
from contextlib import contextmanager

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

        log.info('Making directory "%s"',dir)
        os.mkdir(dir)

def copyfile(source,dest):
    """Helper to copyfile"""
    from shutil import copyfile

    log = logging.getLogger('abaci')
    
    log.debug('Copying "%s" to "%s"',source, dest)
    copyfile(source,dest)
