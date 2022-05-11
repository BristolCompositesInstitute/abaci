import logging
import os
import signal
import time
from abaci.AbaqusJob import AbaqusJob
from abaci.utils import get_current_env_modules

import cPickle as pkl

def get_jobs(args,config):
    """Get list of jobs to run"""

    log = logging.getLogger('abaci')

    output_dir = config['output']

    job_spec = args.job_spec

    log.debug('Job_spec = %s',job_spec)
    
    jobs = []

    # Add any job files specifided in job-spec
    for spec in job_spec:

        if '.inp' in spec:

            job_path = os.path.realpath(spec)

            if os.path.exists(job_path):

                jobs.append(AbaqusJob(output_dir,job_file=job_path))


    # Add any config jobs matching job-spec
    for j in config['job']:

        for spec in job_spec:

            if (spec in j['tags']) or (spec == j['name']):

                jobs.append(AbaqusJob(output_dir,job=j))
                break

    if not jobs:

        log.warning('No jobs were found matching the job-spec "%s"',job_spec)

    else:

        log.debug('Jobs to run = %s',jobs)

    return jobs


def submit_jobs(args,compile_dir,jobs):
    """Submit jobs to cluster job scheduler"""

    modules = get_current_env_modules()

    for job in jobs:

        job.submit_job(compile_dir,modules,'')


def run_jobs(args,compile_dir,jobs):
    """Launch jobs concurrently and wait for completion"""

    launched = []

    def handle_interrupt(signal, frame):
        """Interrupt handler: cancel all jobs"""
        for job in launched:

            job.terminate_job(args.verbose)

        raise Exception('Job execution interrupted')

    # Launch jobs
    for job in jobs:

        # Wait here if already running maximum number of concurrent jobs
        while True:
            n_running = sum([j.is_running() for j in launched])

            if n_running < args.njob:
                break

            time.sleep(0.1)

        job.launch_job(args.nproc,compile_dir)

        launched.append(job)

        signal.signal(signal.SIGINT, handle_interrupt)

    stats = []


    # Wait for all jobs to complete
    while True:

        n_running = sum([j.is_running() for j in launched])

        if n_running == 0:
            break

        time.sleep(0.1)

    # Get job stats
    for job in launched:

        stats.append( job.wait(args.verbose) )

    return stats


def post_process(job_dir,verbose):
    """Post process subcommand for post-processing existing jobs"""

    cache_file = os.path.join(job_dir,'abaci-cache.pkl')

    if not os.path.exists(cache_file):

        raise Exception('Unable to find abaci-cache.pkl file in directory "{dir}"'.format(
            dir=job_dir))

    else:

        with open(cache_file,'r') as f:
            job = pkl.load(f)

        job.run_checks()

        job.post_process(verbose)
