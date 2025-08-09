import logging
import logging.handlers  # pylint: disable=import-error
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional


class EmojiSafeFormatter(logging.Formatter):
    """Formatter that makes emojis safe for console output."""

    # Mapping of emojis to ASCII alternatives
    EMOJI_REPLACEMENTS = {
        "🚀": "[START]",
        "⚙️": "[CONFIG]",
        "🔄": "[PROCESS]",
        "📊": "[STATS]",
        "✅": "[SUCCESS]",
        "❌": "[ERROR]",
        "🔍": "[SEARCH]",
        "⚠️": "[WARNING]",
        "💾": "[SAVE]",
        "🎉": "[COMPLETE]",
    }

    # Cache for emoji support detection
    _emoji_support_cache = None
    _cache_lock = threading.Lock()

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: Literal["%", "{", "$"] = "%",
        validate: bool = True,
    ) -> None:
        super().__init__(fmt, datefmt, style, validate)
        # Check if we're running in a Unicode-compatible terminal
        self.use_emojis = self._check_emoji_support()

    def _check_emoji_support(self) -> bool:
        """Check if the console can handle emoji characters (cached)."""
        with self._cache_lock:
            if self._emoji_support_cache is not None:
                return self._emoji_support_cache

            # Windows Terminal and most modern terminals set this
            if os.getenv("WT_SESSION") or os.getenv("TERM_PROGRAM"):
                self._emoji_support_cache = True
                return True

            # Check if stdout is redirected or if we're in a Unicode-compatible console
            try:
                if sys.stdout.encoding and sys.stdout.encoding.lower() in (
                    "utf-8",
                    "utf8",
                ):
                    self._emoji_support_cache = True
                    return True

                # Try to encode a test emoji to see if it works
                "🔍".encode(sys.stdout.encoding or "utf-8")
                self._emoji_support_cache = True
                return True
            except (UnicodeEncodeError, AttributeError, TypeError):
                self._emoji_support_cache = False
                return False

    def format(self, record: logging.LogRecord) -> str:
        """Format the record with emoji-safe text."""
        # Get the formatted message from the parent formatter
        formatted_msg = super().format(record)

        # If we can't use emojis, replace them with ASCII equivalents
        if not self.use_emojis:
            for emoji, replacement in self.EMOJI_REPLACEMENTS.items():
                formatted_msg = formatted_msg.replace(emoji, replacement)

        return formatted_msg


class AppLoggerFactory:
    """Factory for creating and configuring loggers."""

    _initialized = False
    _verbose = False
    _quiet = False
    _log_dir = "logs"
    _default_log_file: Optional[Path] = None
    _default_stats_file: Optional[Path] = None
    _lock = threading.Lock()
    _configured_loggers: set[str] = set()

    @classmethod
    def initialize(cls, verbose: bool = False, quiet: bool = False) -> None:
        """
        Initialize the logger factory with verbosity settings.

        Args:
            verbose: If True, sets log level to DEBUG
            quiet: If True, sets log level to WARNING
        """
        with cls._lock:
            if cls._initialized:
                return

            cls._verbose = verbose
            cls._quiet = quiet

            try:
                # Create log directory if it doesn't exist
                log_dir = Path(cls._log_dir)
                log_dir.mkdir(parents=True, exist_ok=True)

                timestamp = datetime.now().strftime("%Y-%m-%d")
                cls._default_log_file = log_dir / f"selene_{timestamp}.log"
                cls._default_stats_file = log_dir / f"selene_stats_{timestamp}.log"

                cls.configure_root_logger()
                cls._initialized = True
            except Exception as e:
                raise RuntimeError(f"Failed to initialize logger factory: {e}") from e

    @classmethod
    def update_settings(cls, verbose: bool = False, quiet: bool = False) -> None:
        """
        Update verbosity settings after initialization.

        Args:
            verbose: If True, sets log level to DEBUG
            quiet: If True, sets log level to WARNING
        """
        with cls._lock:
            cls._verbose = verbose
            cls._quiet = quiet
            if cls._initialized:
                cls.configure_root_logger()

    @classmethod
    def create_logger(cls, name: str) -> logging.Logger:
        """
        Create a logger with application-wide consistent settings.

        Args:
            name: Logger name (module path)

        Returns:
            Configured logger
        """
        with cls._lock:
            if not cls._initialized:
                cls.initialize()

            logger = logging.getLogger(name)

            # Only configure if not already configured
            if name not in cls._configured_loggers:
                # Set propagate to True to use root logger's handlers
                logger.propagate = True
                cls._configured_loggers.add(name)

            return logger

    @classmethod
    def get_stats_logger(cls) -> logging.Logger:
        """
        Get a logger specifically for statistics.

        Returns:
            Configured stats logger
        """
        with cls._lock:
            if not cls._initialized or cls._default_stats_file is None:
                raise RuntimeError("Logger factory not initialized")

            stats_logger = logging.getLogger("selene.stats")

            # Clear existing handlers safely
            handlers_to_remove = list(stats_logger.handlers)
            for handler in handlers_to_remove:
                stats_logger.removeHandler(handler)
                try:
                    handler.close()
                except OSError:
                    pass

            try:
                # Use rotating file handler for stats
                file_handler = logging.handlers.RotatingFileHandler(
                    str(cls._default_stats_file),
                    encoding="utf-8",
                    maxBytes=10 * 1024 * 1024,  # 10MB
                    backupCount=5,
                )
                file_handler.setLevel(logging.INFO)
                file_handler.setFormatter(EmojiSafeFormatter("%(message)s"))
                stats_logger.addHandler(file_handler)
                stats_logger.propagate = False  # Don't propagate to root logger
            except Exception as e:
                raise RuntimeError(f"Failed to create stats logger: {e}") from e

            return stats_logger

    @classmethod
    def configure_root_logger(cls) -> None:
        """
        Configure the root logger with the appropriate handlers and level.
        """
        if cls._default_log_file is None:
            raise RuntimeError("Logger factory not initialized")

        root_logger = logging.getLogger()

        # Clear existing handlers safely
        handlers_to_remove = list(root_logger.handlers)
        for handler in handlers_to_remove:
            root_logger.removeHandler(handler)
            try:
                handler.close()
            except OSError:
                pass

        root_logger.setLevel(logging.DEBUG if cls._verbose else logging.INFO)

        console_formatter = EmojiSafeFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        if cls._verbose:
            console_level = logging.DEBUG
        elif cls._quiet:
            console_level = logging.WARNING
        else:
            console_level = logging.INFO

        try:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(console_level)
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

            # Use rotating file handler for main log
            file_handler = logging.handlers.RotatingFileHandler(
                str(cls._default_log_file),
                encoding="utf-8",
                maxBytes=50 * 1024 * 1024,  # 50MB
                backupCount=3,
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            raise RuntimeError(f"Failed to configure root logger: {e}") from e
