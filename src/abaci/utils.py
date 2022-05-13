import logging
import os
import signal
from contextlib import contextmanager
import subprocess
from unicodedata import normalize

def relpathshort(path):
    """
        Returns the shorter of path and relpath
        Avoids issue on Windows for different drive letters
    """

    try:
        rpath = os.path.relpath(path)
    except:
        rpath = path

    return min(path, rpath, key=len)


@contextmanager
def cwd(path, quiet=None):
    """Helper to change directory temporarily"""

    log = logging.getLogger('abaci')

    oldpwd=os.getcwd()
    
    if not quiet:
        log.debug('Changing into directory "%s"',relpathshort(path))

    os.chdir(path)

    try:
        yield
    finally:

        if not quiet:
            log.debug('Changing back to directory "%s"',oldpwd)
            
        os.chdir(oldpwd)


def mkdir(dir):
    """Make a directory, if it doesn't exist"""

    log = logging.getLogger('abaci')

    if os.path.isdir(dir):
        
        log.debug('Directory already exists ("%s")',relpathshort(dir))

    else:

        log.debug('Making directory "%s"',relpathshort(dir))
        os.mkdir(dir)


def copyfile(source,dest):
    """Helper to copyfile"""
    from shutil import copyfile

    log = logging.getLogger('abaci')
    
    log.debug('Copying "%s" to "%s"',relpathshort(source), relpathshort(dest))
    copyfile(source,dest)


def copydir(source,dest):
    """Helper to copy directory"""
    from distutils.dir_util import copy_tree

    log = logging.getLogger('abaci')
    
    log.debug('Copying directory "%s" to "%s"',relpathshort(source), relpathshort(dest))
    copy_tree(source,dest)


def system_cmd(cmd,output=None):
    """Helper to launch system commands"""

    log = logging.getLogger('abaci')

    log.debug('Running command "%s"',' '.join(cmd))

    if output:

        ofile = '{stem}.stdout'.format(stem=output)
        fo = open(ofile,'a')
        log.debug('Command stdout redirected to "%s"',relpathshort(ofile))

        efile = '{stem}.stderr'.format(stem=output)
        fe = open(efile,'a')
        log.debug('Command stderr redirected to "%s"',relpathshort(efile))

    else:

        ofile = None
        efile = None
        
        fo = None
        fe = None

    # Needed on Windows to get return code correctly
    if os.name == 'nt':
        
        cmd.append('&')
        cmd.append('exit')

    p = subprocess.Popen(cmd,stdout=fo,stderr=fe)

    def handle_interrupt(signal, frame):
        p.terminate()
        raise Exception('Command interrupted')

    signal.signal(signal.SIGINT, handle_interrupt)

    return p, ofile, efile


def system_cmd_wait(p,verbosity,ofile=None,efile=None):
    """Wait for system command to finish and check output"""

    log = logging.getLogger('abaci')

    p.communicate()

    # Print outputs if (non-zero status and not in quiet mode) or
    #  if in very verbose mode
    if (p.returncode != 0 and verbosity > -1) or verbosity > 1:

        if ofile:

            with open(ofile, "r") as fo:

                o = fo.readlines()

            print ''.join(o)
        
        if efile:

            with open(efile, "r") as fe:

                e = fe.readlines()

            print ''.join(e)

    return p.returncode


def to_ascii(ustring):

    return normalize('NFKD',ustring).encode('ascii','ignore')


def recurse_files(path):

    filelist = []

    if os.path.isdir(path):

        for currentpath, folders, files in os.walk(path):

            for file in files:
                        
                filelist.append(os.path.join(currentpath, file))

    else:

        filelist = [path]

    return filelist


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


def get_current_env_modules():
    """Get a list of environment modules in current env"""

    # (module command is a bash alias)
    cmd = ['bash','-c','module -t list']
    
    try:

        p =  subprocess.Popen(cmd,stderr=subprocess.PIPE)

        stdout, stderr = p.communicate()

        modules = stderr.strip().split('\n')

    except:

        modules = None

    return modules
    

def prompt_input_default(prompt,default):
    """Interactively prompt user for input with editable default"""

    # readline module doesn't work with abaqus python
    #  so use bash instead (never used on Windows)

    if not default:

        default = ''

    cmd = ['bash','-c','read -r -p "{p}" -e -i "{d}" && echo $REPLY'.format(
            p=prompt,d=default)]

    p =  subprocess.Popen(cmd,stdout=subprocess.PIPE)

    stdout, stderr = p.communicate()

    if p.returncode != 0:

        raise Exception('Interactive input prompt cancelled by user')

    stdout = stdout.strip()

    if len(stdout) < 1:
        
        stdout = None
        
    elif isinstance(default, int):

        stdout = int(stdout)
   
    return stdout

  