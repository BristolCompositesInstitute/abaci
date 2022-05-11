import os
from os.path import join
import subprocess
from abaci.utils import cwd, system_cmd, system_cmd_wait

def check_for_abaqus():
    """Check for Abaqus and raise Exception if not found"""

    if not have_abaqus():

        raise Exception('Abaqus not found, cannot continue.')


def have_abaqus():
    """Check if abaqus is available in current environment"""

    devnull = open(os.devnull,'w')

    cmd = abaqus_cmd(['information=version'])
    
    try:

        stat =  subprocess.call(cmd,stdout=devnull,stderr=devnull)

    except:

        stat = -1

    return stat == 0


def run(dir,job_name,mp_mode,nproc):
    """Helper to launch an Abaqus job"""

    cmd = get_run_cmd(job_name,mp_mode,nproc)

    with cwd(dir):

        p, ofile, efile = system_cmd(cmd,output=join(dir,'abaqus'))

    return p, ofile, efile


def get_run_cmd(job_name,mp_mode,nproc):
    """Helper to construct an Abaqus job command"""

    args = []
    args.append('job={name}'.format(name=job_name))

    if mp_mode != 'disable' and nproc > 0:

        args.append('mp_mode={mode}'.format(mode=mp_mode))
        args.append('cpus={n}'.format(n=nproc))

    args.append('double')
    args.append('interactive')

    return abaqus_cmd(args)


def terminate(dir, job_name):
    """Terminate a running Abaqus job"""

    args = ['terminate']
    args.append('job={name}'.format(name=job_name))

    cmd = abaqus_cmd(args)

    with cwd(dir):

        p, ofile, efile = system_cmd(cmd,output=join(dir,'abaqus-terminate'))

    return p, ofile, efile


def make(dir, lib_file, verbosity):
    """Invoke Abaqus make command"""

    args = ['make']
    args.append('library={file}'.format(file=os.path.basename(lib_file)))

    cmd = abaqus_cmd(args)

    with cwd(dir):

        p,ofile,efile = system_cmd(cmd, output=os.path.join(dir,'abaqus-make'))

        stat = system_cmd_wait(p,verbosity,ofile,efile)

    return stat


def abaqus_cmd(args):
    """Build abaqus launch command"""

    cmd = ['abaqus'] + args

    if os.name == 'nt':
                
        cmd[0] = 'c:\\SIMULIA\\Commands\\abaqus.bat'

    return cmd