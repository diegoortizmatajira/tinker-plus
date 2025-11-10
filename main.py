"""
Main entry point for the Tinker-Plus application.
"""

import logging
from core.runtime_provider import RuntimeProvider
from features.proton_selection import ProtonSelection


def main():
    """
    The main entry point for the application.

    This function initializes the runtime environment and configures it
    with the ProtonSelection feature. It then triggers the runtime
    execution.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("tinker-plus")
    logger.info("Starting Tinker-Plus application...")
    try:
        runtime = RuntimeProvider([ProtonSelection()])
        runtime.build_configuration()
        runtime.run()
    except RuntimeError as e:
        logger.error("An error occurred during runtime execution. %s", e)
    logger.info("Tinker-Plus application finished.")


if __name__ == "__main__":
    main()
