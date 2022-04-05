from abaci.cli import parse_cli, init_logger, init_logger_file
from abaci.config import load_config
from abaci.compile import compile_user_subroutine, collect_cov_report
from abaci.jobs import get_jobs, run_jobs
from abaci.utils import mkdir, daemonize
from abaci.dependencies import fetch_dependencies
from abaci.show_info import show_info

def main():
    """Main entry point for abaci program"""

    args = parse_cli()

    init_logger(args.verbose)

    config, config_dir = load_config(args.config,False)
         
    dep_list = fetch_dependencies(config, config_dir, args.verbose)

    if args.action == 'show':

        show_info(args, config, dep_list)

        exit()

    mkdir(config['output'])

    init_logger_file(log_dir=config['output'])

    stat, compile_dir = compile_user_subroutine(args, config['output'], 
                        config['user-sub-file'], config['compile'], dep_list)

    if args.action == 'compile' or stat != 0:
        return

    jobs = get_jobs(args,config)

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