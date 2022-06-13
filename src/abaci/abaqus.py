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


def get_mpi_job_allocation_cmd():
    """Return the bash commands for extracting node allocation for Abaqus mpi"""

    cmd = ['env_file=abaqus_v6.env']
    cmd.append(r'node_list=$(scontrol show hostname ${SLURM_NODELIST} | sort -u)')
    cmd.append(r'mp_host_list="["')
    cmd.append(r'for host in ${node_list}; do')
    cmd.append('    mp_host_list="${mp_host_list}[\'$host\', ${SLURM_CPUS_ON_NODE}],"')
    cmd.append(r'done')
    cmd.append(r'mp_host_list=$(echo ${mp_host_list} | sed -e "s/,$/]/")')
    cmd.append(r'echo ""  >> ${env_file}')
    cmd.append(r'echo "mp_host_list=${mp_host_list}"  >> ${env_file}')

    return cmd

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

    if os.name == 'nt':
        args.append('directory="{dir}"'.format(dir=dir))
    else:
        args.append('directory={dir}'.format(dir=dir))     # (Can't quote path on linux for some reason)


    cmd = abaqus_cmd(args)

    with cwd(dir):

        p,ofile,efile = system_cmd(cmd, output=os.path.join(dir,'abaqus-make'))

        stat = system_cmd_wait(p,verbosity,ofile,efile)

    return stat


def abaqus_cmd(args,noshell=None):
    """Build abaqus launch command"""

    cmd = ['abaqus'] + args

    if os.name == 'nt':
                
        cmd[0] = 'c:\\SIMULIA\\Commands\\abaqus.bat'

        # Needed on Windows to get return code correctly
        if not noshell:
            cmd.append('&')
            cmd.append('exit')

    return cmd