import os
import tempfile
import subprocess
from abaci.utils import cwd, system_cmd, system_cmd_wait

def clone(git_path,working_dir,target_dir,verbosity):
    """Clone a git repository"""
    fh,git_log_file = tempfile.mkstemp()
    os.close(fh)

    with cwd(working_dir):

        git_cmd = ['git', 'clone', git_path, target_dir]

        p, ofile, efile = system_cmd(git_cmd,output=git_log_file)
        
        stat = system_cmd_wait(p, verbosity, ofile, efile)

        if stat:

            raise Exception('Error while cloning repository {repo}'.format(repo=git_path))


def checkout(git_path,git_ref,verbosity):
    """Checkout a branch/tag/commit in an existing local repository"""
    fh,git_log_file = tempfile.mkstemp()
    os.close(fh)

    with cwd(git_path):

        git_cmd = ['git', 'checkout', git_ref]

        p, ofile, efile = system_cmd(git_cmd,output=git_log_file)
        
        stat = system_cmd_wait(p, verbosity, ofile, efile)

        if stat:

            raise Exception('Error while checking out reference {ref} in {repo}'.format(
                                ref=git_ref,repo=git_path))

    return stat


def is_head_detached(git_path):
    """Check if HEAD is detached in a local repository"""

    devnull = open(os.devnull,'w')
    
    with cwd(git_path):

        git_cmd = ['git', 'symbolic-ref', '-q', 'HEAD']
                
        stat =  subprocess.call(git_cmd,stdout=devnull,stderr=devnull)

    return stat != 0


def is_dirty(git_path):
    """Check if git repository has unstaged changes"""

    with cwd(git_path):

        git_cmd = ['git', 'diff', '--quiet']
        
        p, ofile, efile = system_cmd(git_cmd)
                
        stat = system_cmd_wait(p, verbosity=-1)

    return stat != 0


def current_commit(git_path):
    """Get the current commit of HEAD"""

    with cwd(git_path):

        git_cmd = ['git', 'show', '--format=%H', '-s']
        
        return subprocess.check_output(git_cmd).strip()


def show_ref(git_path,ref):
    """Return the git commit for reference (tag)"""

    with cwd(git_path):

        git_cmd = ['git', 'show-ref', '-s', ref]
        
        return subprocess.check_output(git_cmd).strip()


def get_tag(git_path):
    """Return the git tag for current commit """

    with cwd(git_path):

        git_cmd = ['git', 'describe', '--tags', 'HEAD']
        
        return subprocess.check_output(git_cmd).strip()


def init_bare(path):
    """Initialise a bare git repo at the local path"""

    devnull = open(os.devnull,'w')

    with cwd(path):

        git_cmd = ['git', 'init', '--bare']
        
        subprocess.check_call(git_cmd,stdout=devnull,stderr=devnull)


def add_and_commit(path,message):
    """Helper to add all and commit"""

    devnull = open(os.devnull,'w')

    with cwd(path):
        
        subprocess.check_call(['git', 'add', '-A'],stdout=devnull,stderr=devnull)

        subprocess.check_call(['git', 'commit', '-m', message,'--allow-empty'],stdout=devnull,stderr=devnull)


def add_tag(path,tag):
    """Helper to tag commit"""
    
    with cwd(path):

        subprocess.check_call(['git', 'tag', tag])


def push(path):
    """Helper to push master to remote with tags"""

    devnull = open(os.devnull,'w')

    with cwd(path):

        subprocess.check_call(['git', 'push','--tags', 'origin', 'master'],stdout=devnull,stderr=devnull)


def pull(path):
    """Helper to pull from default remote"""

    devnull = open(os.devnull,'w')

    with cwd(path):

        subprocess.check_call(['git', 'pull']) #,stdout=devnull,stderr=devnull)