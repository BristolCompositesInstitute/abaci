from abaci.cli import parse_cli, init_logger, init_logger_file
from abaci.config import load_config, list_config_jobs
from abaci.compile import compile_user_subroutine, collect_cov_report
from abaci.jobs import get_jobs, run_jobs
from abaci.utils import mkdir, daemonize
from abaci.dependencies import fetch_dependencies

def main():
    """Main entry point for abaci program"""

    args = parse_cli()

    init_logger(args.verbose)

    config, config_dir = load_config(args.config,args.echo)

    mkdir(config['output'])

    init_logger_file(log_dir=config['output'])

    if args.list:
        list_config_jobs(config,args.verbose)
        exit()

    dep_list = fetch_dependencies(config, config_dir, args.verbose)

    jobs = get_jobs(args,config)

    stat, compile_dir = compile_user_subroutine(args, config['output'], 
                        config['user-sub-file'], config['compile'], dep_list)

    if args.compile or stat != 0:
        return

    if args.background:
        daemonize()

    stats = run_jobs(args,compile_dir,jobs)

    for job, stat in zip(jobs,stats):

        if stat == 0:

            job.run_checks()

    if args.codecov or config['compile']['code-coverage']:
        
        collect_cov_report(config,compile_dir,args.verbose)


if __name__ == "__main__":
    main()