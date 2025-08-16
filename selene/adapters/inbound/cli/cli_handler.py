from pathlib import Path
from typing import Any, Optional

import yaml

from selene.adapters.inbound.cli.argument_parser import ArgumentParser, CLIArguments
from selene.application.containers.market_data_container import MarketDataContainer
from selene.infrastructure.logging.logger_factory import AppLoggerFactory


class CLIHandler:
    """Handles command-line interface concerns."""

    def __init__(self) -> None:
        self.argument_parser = ArgumentParser()
        self.logger_factory = AppLoggerFactory
        self.logger_factory.initialize(verbose=False, quiet=False)
        self.logger = self.logger_factory.create_logger(__name__)

    def run(self, args: Optional[list] = None) -> int:
        """Main CLI entry point."""
        try:
            parsed_args = self.argument_parser.parse(args)

            self.logger_factory.update_settings(
                verbose=parsed_args.verbose, quiet=parsed_args.quiet
            )

            self._validate_arguments(parsed_args)

            return self._route_command(parsed_args)

        except FileNotFoundError as e:
            return self._handle_error(f"Configuration file not found: {e}", 1)
        except ValueError as e:
            return self._handle_error(f"Invalid configuration: {e}", 2)
        except (OSError, yaml.YAMLError) as e:
            self.logger.exception("Unhandled exception")
            return self._handle_error(f"Application error: {e}", 3)

    def _validate_arguments(self, args: CLIArguments) -> None:
        """Validate CLI arguments."""
        if not args.config:
            raise ValueError("Configuration file is required")

        config_path = Path(args.config)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file '{args.config}' not found")

    def _load_yaml_config(self, config_path: str) -> Any:
        with open(config_path, "r", encoding="utf-8") as file:
            config_data = yaml.safe_load(file)

        return config_data

    def _handle_run_command(self, _args: CLIArguments) -> int:
        self.logger.info("Run command is not implemented yet")
        return 0

    def _handle_load_command(self, _args: CLIArguments) -> int:
        self.logger.info("Load command is not implemented yet")
        return 0

    def _handle_status_command(self, _args: CLIArguments) -> int:
        self.logger.info("Status command is not implemented yet")
        return 0

    def _handle_fetch_command(self, args: CLIArguments) -> int:
        if not args.config:
            raise ValueError("Configuration file is required for 'fetch' command")

        # Create and run application
        container = MarketDataContainer(args.config)
        use_case = container.create_use_case()

        try:
            result = use_case.execute()
            success_rate = result["summary"]["success_rate"]
            self.logger.info(
                "Fetching complete. Success rate: %.2f%%", success_rate * 100
            )
        finally:
            container.cleanup()  # Ensure connections are closed

        return 0

    def _route_command(self, args: CLIArguments) -> int:
        """Route command to appropriate handler."""
        command_handlers = {
            "run": self._handle_run_command,
            "load": self._handle_load_command,
            "status": self._handle_status_command,
            "fetch": self._handle_fetch_command,
        }

        handler = command_handlers.get(args.command)
        if handler:
            return handler(args)
        else:
            return self._handle_error(f"Unknown command: {args.command}", 1)

    def _handle_error(self, message: str, exit_code: int) -> int:
        """Standardized error handling."""
        self.logger.error("❌ %s", message)
        return exit_code
