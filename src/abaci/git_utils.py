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

            raise Exception('Error while cloning repository {repo}'.format(repo=dep_git))


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
    with cwd(git_path):

        git_cmd = ['git', 'symbolic-ref', '-q', 'HEAD']
        
        p, ofile, efile = system_cmd(git_cmd)
                
        stat = system_cmd_wait(p, verbosity=-1)

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