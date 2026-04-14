"""
Logger - Logging utility dengan rotasi file
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from config import LOG_CONFIG


def setup_logger(
    name: str = "emulator_translator",
    level: str = None,
    log_file: str = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Setup logger dengan file dan console handler
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path ke log file
        console_output: Apakah output ke console juga
        
    Returns:
        Configured logger instance
    """
    if level is None:
        level = LOG_CONFIG["level"]
    
    if log_file is None:
        log_file = LOG_CONFIG["file"]
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Clear existing handlers
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(LOG_CONFIG["format"])
    
    # File handler dengan rotasi
    try:
        # Ensure log directory exists
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=LOG_CONFIG["max_file_size"],
            backupCount=LOG_CONFIG["backup_count"],
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file handler: {e}")
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)  # Console hanya INFO+
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get existing logger atau buat baru dengan default settings
    
    Args:
        name: Logger name (None untuk root logger)
        
    Returns:
        Logger instance
    """
    if name is None:
        return logging.getLogger("emulator_translator")
    
    # Cek jika logger sudah ada
    logger = logging.getLogger(name)
    
    # Jika belum ada handlers, setup dulu
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


def log_exception(logger: logging.Logger, exc: Exception, context: str = ""):
    """
    Log exception dengan traceback lengkap
    
    Args:
        logger: Logger instance
        exc: Exception yang terjadi
        context: Context message
    """
    import traceback
    
    error_msg = f"{context}: {str(exc)}" if context else str(exc)
    logger.error(error_msg, exc_info=True)
    
    # Juga log traceback lengkap ke file
    tb = traceback.format_exc()
    logger.debug(f"Full traceback:\n{tb}")


class LogManager:
    """Manager untuk multiple loggers"""
    
    def __init__(self):
        self.loggers = {}
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get atau create logger"""
        if name not in self.loggers:
            self.loggers[name] = setup_logger(name)
        return self.loggers[name]
    
    def set_level(self, name: str, level: str):
        """Ubah log level untuk logger tertentu"""
        if name in self.loggers:
            self.loggers[name].setLevel(getattr(logging, level))
    
    def get_all_loggers(self) -> list:
        """Dapatkan semua logger yang terdaftar"""
        return list(self.loggers.keys())


# Default logger instance
default_logger = setup_logger()
