"""
Emulator Game Translator - Main Entry Point
Auto-translate game ROM untuk emulator Android
"""

import sys
import logging
from config import GUI_CONFIG, APP_INFO, LOG_CONFIG


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, LOG_CONFIG["level"]),
        format=LOG_CONFIG["format"],
        handlers=[
            logging.FileHandler(LOG_CONFIG["file"]),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def main():
    """Main application entry point"""
    # Setup logging
    logger = setup_logging()
    logger.info(f"Starting {APP_INFO['name']} v{APP_INFO['version']}")

    try:
        # Initialize GUI
        from gui.main_window import MainWindow
        app = MainWindow()
        logger.info("GUI initialized successfully")

        # Run application
        app.mainloop()

    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
