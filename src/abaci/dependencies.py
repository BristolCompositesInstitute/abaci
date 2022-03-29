import os
import logging
from abaci import git_utils as git
from abaci.config import load_config
from abaci.utils import cwd, mkdir, system_cmd, system_cmd_wait

def fetch_dependencies(config, config_dir, verbosity):
    """Breadth-first fetching of project dependencies via git"""

    dependencies = config['dependency']

    deps_dir = os.path.join(config_dir,'dependencies')

    if not os.path.isdir(deps_dir):

        mkdir(deps_dir)

    while dependencies:

        dep = dependencies.pop(0)

        dep_path = fetch_dependency(deps_dir,dep['name'],dep['git'],dep['version'],verbosity)
        
        with cwd(dep_path):
            
            dep_config_file = os.path.join(dep_path,'abaci.toml')

            dep_config, dep_config_dir = load_config(dep_config_file, echo=False)

            dependencies.extend(dep_config['dependency'])


def fetch_dependency(deps_dir,dep_name,dep_git,dep_version,verbosity):
    """Fetch a single dependency via git and return path to local repository"""

    log = logging.getLogger('abaci')

    dep_path = os.path.join(deps_dir,dep_name)

    if not os.path.isdir(dep_path):

        log.info('Fetching dependency "{dep}" ({ver})'.format(dep=dep_name,ver=dep_version))

        git.clone(dep_git,deps_dir,dep_name,verbosity)

        git.checkout(dep_path,dep_version,verbosity)


    if not git.is_head_detached(dep_path):

        log.warning('(!) Warning, dependency {dep} is not pinned to a specific commit/tag - the current configuration is not reproducible.'.format(dep=dep_name))

    is_dirty = git.is_dirty(dep_path)
    if is_dirty:

        log.warning("(!) Warning, dependency {dep} has modified code - the current configuration is not reproducible.\n\t"
                        "To ensure others to use your changes, commit them to the upstream repository at:\n\t {upstream}".format(dep=dep_name,upstream=dep_git))

    commit = git.current_commit(dep_path)

    needs_update = False
    if commit != dep_version:

        dep_version_commit = git.show_ref(dep_path,dep_version)

        if commit != dep_version_commit:

            needs_update = True

    if needs_update and is_dirty:

        log.warning("(!) Warning, dependency {dep} cannot be updated to version '{ver}' because it contains modified code.\n\t".format(
                     dep=dep_name,ver=dep_version))

    elif needs_update:

        log.info('Updating dependency "{dep}" to {ver}'.format(dep=dep_name,ver=dep_version))

        git.checkout(dep_path,dep_version,verbosity)

    commit = git.current_commit(dep_path)
    log.debug('Dependency {dep} is at commit {h}'.format(dep=dep_name,h=commit))

    return dep_path



