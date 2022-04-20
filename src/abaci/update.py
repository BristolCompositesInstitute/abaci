from genericpath import exists
import os
from os.path import join, dirname, pardir, realpath, exists
from shutil import rmtree
import argparse
from tempfile import mkdtemp
import logging

from abaci.ssh_utils import is_ssh_url, setup_ssh_agent
import abaci.git_utils as git
from abaci.utils import copydir, copyfile
import abaci.cli

_DEFAULT_UPSTREAM = 'git@github.com:BristolCompositesInstitute/abaci.git'
_DEFAULT_REF = 'main'

class UpdateAction(argparse.Action):
    """Argparse action for --update"""

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(UpdateAction, self).__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):

        abaci.cli.init_logger(verbose=2)

        log = logging.getLogger('abaci')

        install_location = realpath(join(dirname(realpath(__file__)), pardir, pardir))

        log.info('Install location: "%s"', install_location)

        git_ref, upstream = parse_update_arg(values)

        log.info('Fetching ref "%s" from upstream: "%s"', git_ref, upstream)

        update_abaci(install_location,upstream,git_ref)

        exit(0)


def parse_update_arg(value):
    """Parse [[REPO:]GITREF] from CLI"""

    if not value:

        upstream = _DEFAULT_UPSTREAM
        git_ref = _DEFAULT_REF

    else:

        if ':' in value:

            parts = value.split(':')

            upstream = parts[0]
            git_ref = parts[1]

        else:

            upstream = _DEFAULT_UPSTREAM
            git_ref = value

    return git_ref, upstream


def update_abaci(install_location,upstream,git_ref):
    """Clone abaci into temporary dir and copy sources to local installation"""

    log = logging.getLogger('abaci')
    
    if is_ssh_url(upstream):
    
        setup_ssh_agent()
    
    if git.isa_git_repo(install_location):

        if git.is_dirty(install_location):

            log.fatal('Unable to update abaci since running from git repository which contains changes')

        else:

            git.fetch(install_location)
            git.checkout(install_location,git_ref,verbosity=1)

            exit(0)

    else:

        clone_dir = mkdtemp()

        git.clone(upstream,clone_dir,'abaci',verbosity=2)
        git_dir = join(clone_dir,'abaci')

        git.checkout(git_dir,git_ref,verbosity=1)

        lib_src = join(git_dir,'src')
        lib_dest = join(install_location,'abaci')

        if exists(lib_dest):

            rmtree(lib_dest)

        copydir(lib_src,lib_dest)

        if os.name == 'nt':

            ABAQUS_INSTALL = 'c:\SIMULIA\Commands'
            copyfile(join(git_dir,'scripts','abaci.cmd'),join(ABAQUS_INSTALL,'abaci.cmd'))

        else:

            launcher = join(install_location,pardir,'bin','abaci')
            copyfile(join(git_dir,'scripts','abaci'),launcher)