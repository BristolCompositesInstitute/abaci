import os
import logging
from abaci import git_utils as git
from abaci.config import load_config
from abaci.utils import mkdir
from abaci.ssh_utils import setup_ssh_agent, is_ssh_url


def fetch_dependencies(config, config_dir, verbosity):
    """Breadth-first fetching of project dependencies via git"""
    
    # Enqueue dependencies from the root project
    dependencies = list(config['dependency'])

    if not dependencies:

        return {}

    if not git.have_git:

        raise Exception('git not found, cannot continue: git is required to fetch dependencies.')

    deps_dir = os.path.join(config_dir,'dependencies')

    if not os.path.isdir(deps_dir):

        mkdir(deps_dir)

    dep_list = {}

    while dependencies:

        dep = dependencies.pop(0)

        if dep['name'] not in dep_list:

            dep_path = fetch_dependency(deps_dir,dep['name'],dep['git'],dep['version'],verbosity)
                
            dep_config_file = os.path.join(dep_path,'abaci.toml')

            dep_config, dep_config_dir = load_config(dep_config_file, echo=False)

            # Check specified name matches that in package config
            if dep['name'] != dep_config['name']:

                raise Exception('Dependency name mismatch for "{n1}", found name="{n2}" in dependency manifest'.format(
                                n1=dep['name'],n2=dep_config['name']))

            dep_list[dep['name']] = {'local_path': dep_path, 
                                     'config': dep_config,
                                     'git': dep['git'],
                                     'version': dep['version'],
                                     'includes': dep_config['compile']['include']}
            
            # Enqueue dependencies from this dependency
            dependencies.extend(dep_config['dependency'])
    
    return dep_list


def fetch_dependency(deps_dir,dep_name,dep_git,dep_version,verbosity):
    """Fetch a single dependency via git and return path to local repository"""

    log = logging.getLogger('abaci')

    dep_path = os.path.join(deps_dir,dep_name)

    if is_ssh_url(dep_git):
            
        setup_ssh_agent()
            
    if not os.path.isdir(dep_path):

        log.info('Fetching dependency "{dep}" ({ver})'.format(dep=dep_name,ver=dep_version))

        git.clone(dep_git,deps_dir,dep_name,verbosity)

        git.checkout(dep_path,dep_version,verbosity)

    is_dirty = git.is_dirty(dep_path)
    if is_dirty:

        log.warning("(!) Warning, dependency {dep} has modified code - the current configuration is not reproducible.\n\t"
                        "To ensure others to use your changes, commit them to the upstream repository at:\n\t {upstream}".format(dep=dep_name,upstream=dep_git))

    current_tag = git.get_tag(dep_path)
    current_commit = git.current_commit(dep_path)
    
    needs_update = not git.is_head_detached(dep_path) or \
        (current_commit != dep_version and current_tag != dep_version)

    if needs_update:

        if is_dirty:

            log.warning("(!) Warning, dependency {dep} cannot be updated to version '{ver}' because it contains modified code.\n\t".format(
                        dep=dep_name,ver=dep_version))

        else:

            log.info('Updating dependency "{dep}" to {ver}'.format(dep=dep_name,ver=dep_version))

            git.fetch(dep_path)
            git.checkout(dep_path,dep_version,verbosity)
            
            # Merge changes from upstream if on a branch
            if not git.is_head_detached(dep_path):
                
                git.merge_remote(dep_path)

    if not git.is_head_detached(dep_path):

        log.warning('(!) Warning, dependency {dep} is not pinned to a specific commit/tag - the current configuration is not reproducible.'.format(dep=dep_name))

    current = git.get_tag(dep_path) or git.current_commit(dep_path)
    log.debug('Dependency {dep} is at {h}'.format(dep=dep_name,h=current))

    return dep_path



