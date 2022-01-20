import logging
import os
from abaci.cli import parse_cli, init_logger
from abaci.config import load_config
from abaci.AbaqusJob import AbaqusJob
from abaci.compile import compile_user_subroutine, collect_cov_report
from abaci.utils import mkdir

def main():
    """Main entry point for abaci program"""

    args = parse_cli()

    init_logger(args)

    config = load_config(args)

    jobs = get_jobs(args,config)

    mkdir(config['output'])

    compile_dir = compile_user_subroutine(args,config)

    if args.compile:
        return

    for job in jobs:

        job.run_job(compile_dir)

    if args.codecov or config['compile']['code-coverage']:
        collect_cov_report(config,compile_dir)


def get_jobs(args,config):
    """Get list of jobs to run"""

    log = logging.getLogger('abaci')

    output_dir = config['output']

    job_spec = args.job_spec

    log.info('Job_spec = %s',job_spec)
    
    jobs = []

    # Add any job files specifided in job-spec
    for spec in job_spec:

        if '.inp' in spec:

            job_path = os.path.realpath(spec)

            if os.exists(job_path):

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


if __name__ == "__main__":
    main()