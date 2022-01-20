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