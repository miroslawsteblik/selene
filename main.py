import sys

from selene.adapters.cli.cli_handler import CLIHandler


def main() -> None:
    """Main entry point - delegates to CLI adapter."""

    cli_handler = CLIHandler()
    exit_code = cli_handler.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()


# selene --help
# selene run --config path/to/config.yaml
