import logging
import os
import signal
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


def system_cmd(cmd,verbosity,output=None):
    """Helper to launch system commands"""

    log = logging.getLogger('abaci')

    log.debug('Running command "%s"',' '.join(cmd))

    p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    def handle_interrupt(signle, frame):
        p.terminate()
        raise Exception('Command interrupted')

    signal.signal(signal.SIGINT, handle_interrupt)

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

    if output:

        with open('{stem}.stdout'.format(stem=output), "w") as f:

            f.write(o)

        with open('{stem}.stderr'.format(stem=output), "w") as f:

            f.write(e)

    return p.returncode
    

def to_ascii(ustring):

    return normalize('NFKD',ustring).encode('ascii','ignore')


def daemonize():
   """Use 'double-fork magic' to detach from the controlling terminal and run in the
   background as a daemon.
   
   Source: https://stackoverflow.com/a/5976352 (CC BY-SA 3.0.)
   """

   try:
      # Fork a child process so the parent can exit.
      pid = os.fork()
   except OSError as e:
      raise Exception("%s [%d]".format(e.strerror, e.errno))

   if (pid == 0):   # The first child.
      # To become the session leader of this new session and the process group
      # leader of the new process group, we call os.setsid().  The process is
      # also guaranteed not to have a controlling terminal.
      os.setsid()

      try:
         # Fork a second child and exit immediately to prevent zombies.  This
         # causes the second child process to be orphaned, making the init
         # process responsible for its cleanup. 
         pid = os.fork()    # Fork a second child.
      except OSError as e:
         raise Exception("%s [%d]".format(e.strerror, e.errno))

      if (pid == 0):    # The second child continues
        pass
      else:
         os._exit(0)    # Exit the first child
   else:
      os._exit(0)   # Exit parent of the first child.