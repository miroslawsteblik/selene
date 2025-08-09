import argparse
from dataclasses import dataclass
from typing import Optional


@dataclass
class CLIArguments:
    """Parsed CLI arguments."""

    command: str  # The main command (run, load, status)
    config: Optional[str] = None
    verbose: bool = False
    quiet: bool = False
    output_format: str = "csv"
    # options: Dict[str, Any] = None


class ArgumentParser:
    """Handles command-line argument parsing."""

    def __init__(self) -> None:
        self._parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with all options."""
        parser = argparse.ArgumentParser(
            prog="selene",
            description="Advanced data processing pipeline",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  selene run --config config/csv_mapping.yaml
  selene load --config config/db_load.yaml
  selene status --last
            """,
        )

        subparsers = parser.add_subparsers(
            title="Commands",
            description="Available commands",
            dest="command",
            required=True,
        )
        # Define common arguments that all commands will inherit
        parent_parser = argparse.ArgumentParser(add_help=False)

        # Global arguments
        parent_parser.add_argument(
            "--verbose", "-v", action="store_true", help="Enable verbose output"
        )

        parent_parser.add_argument(
            "--quiet",
            "-q",
            action="store_true",
            help="Suppress all output except errors",
        )

        parent_parser.add_argument(
            "--output-format",
            choices=["csv", "json", "excel"],
            default="csv",
            help="Output format for results (default: csv)",
        )

        # Add subcommands
        run_parser = subparsers.add_parser(
            "run",
            help="Run the data pipeline",
            parents=[parent_parser],
        )
        run_parser.add_argument(
            "--config",
            "-c",
            required=True,
            type=str,
            help="Configuration file",
        )

        status_parser = subparsers.add_parser(
            "status",
            help="Check the status of the last run",
            parents=[parent_parser],
        )
        status_parser.add_argument(
            "--last",
            action="store_true",
            help="Show status of the last run",
        )

        load_parser = subparsers.add_parser(
            "load",
            help="Load data from a source",
            parents=[parent_parser],
        )
        load_parser.add_argument(
            "--config",
            "-c",
            required=True,
            type=str,
            help="Configuration file",
        )

        fetch_parser = subparsers.add_parser(
            "fetch",
            help="Fetch data from API and load to database",
            parents=[parent_parser],
        )
        fetch_parser.add_argument("--config", help="Configuration file")

        return parser

    def parse(self, args: Optional[list] = None) -> CLIArguments:
        """Parse command line arguments."""
        parsed = self._parser.parse_args(args)

        # Create a dictionary for command-specific options
        options = {}

        # Add command-specific options
        if hasattr(parsed, "validate_only"):
            options["validate_only"] = parsed.validate_only
        if hasattr(parsed, "last"):
            options["last"] = parsed.last
        if hasattr(parsed, "sslmode") and parsed.sslmode:
            options["sslmode"] = parsed.sslmode

        # Convert to our dataclass
        return CLIArguments(
            command=parsed.command,
            config=parsed.config,
            verbose=parsed.verbose if hasattr(parsed, "verbose") else False,
            quiet=parsed.quiet if hasattr(parsed, "quiet") else False,
            output_format=(
                parsed.output_format if hasattr(parsed, "output_format") else "csv"
            ),
            # options=options
        )
