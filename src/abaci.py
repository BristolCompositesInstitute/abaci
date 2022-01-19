from cli import parse_cli, init_logger
def main():
    """Main entry point for abaci program"""

    args = parse_cli()

    init_logger(args)


if __name__ == "__main__":
    main()