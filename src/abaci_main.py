from abaci.cli import parse_cli, init_logger
from abaci.config import load_config

def main():
    """Main entry point for abaci program"""

    args = parse_cli()

    init_logger(args)

    config = load_config(args)

if __name__ == "__main__":
    main()