"""
Main entry point for the Tinker-Plus application.
"""

from core.runtime_provider import RuntimeProvider
from features.proton_selection import ProtonSelection


def main():
    """
    The main entry point for the application.

    This function initializes the runtime environment and configures it
    with the ProtonSelection feature. It then triggers the runtime
    execution.
    """
    print("Hello from tinker-plus!")
    runtime = RuntimeProvider([ProtonSelection()])
    runtime.build_configuration()
    runtime.run()


if __name__ == "__main__":
    main()
