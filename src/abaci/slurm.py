import os
import subprocess
from abaci.utils import cwd

def have_slurm():

    devnull = open(os.devnull,'w')

    cmd = ['sinfo','--version']
    
    try:

        stat =  subprocess.call(cmd,stdout=devnull,stderr=devnull)

    except:

        stat = -1

    return stat == 0


def spool_job_script(script_path,modules,cmds,job_name,time,nodes=None,partition=None,
    tasks_per_node=None,cpus_per_task=None,mem_per_cpu=None,email=None):
    """Write out a SLURM job script"""

    with open(script_path,'w') as f:

        f.write('#!/bin/sh\n')

        f.write('#SBATCH --job-name={name}\n'.format(name=job_name))

        f.write('#SBATCH --time={time}\n'.format(time=time))

        if partition:
            f.write('#SBATCH --partition={part}\n'.format(part=partition))

        if nodes:
            f.write('#SBATCH --nodes={nodes}\n'.format(nodes=nodes))

        if tasks_per_node:
            f.write('#SBATCH --tasks-per-node={tasks}\n'.format(tasks=tasks_per_node))

        if cpus_per_task:
            f.write('#SBATCH --cpus-per-task={cpus}\n'.format(cpus=cpus_per_task))

        if mem_per_cpu:
            f.write('#SBATCH --mem-per-cpu={mem}\n'.format(mem=mem_per_cpu))

        if email:
            f.write('#SBATCH --mail-type=FAIL,END\n')
            f.write('#SBATCH --mail-user={email}\n'.format(email=email))

        f.write('')

        for mod in modules:

            f.write('module load {mod}\n'.format(mod=mod))

        f.write('unset SLURM_GTIDS\n')

        for cmd in cmds:

            f.write(cmd+'\n')


def submit_job(working_dir,script_path,args):

    with cwd(working_dir):

        cmd = ['sbatch',script_path]
        cmd.extend(args)
        
        p =  subprocess.Popen(cmd,stdout=subprocess.PIPE)

        stdout, stderr = p.communicate()

        job_id = stdout.split()[-1]

        return job_id


            
