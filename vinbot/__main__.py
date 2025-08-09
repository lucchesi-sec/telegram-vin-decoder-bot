"""
Main entry point for running vinbot as a module.
"""

from .bot import run

if __name__ == "__main__":
    # Call run() directly instead of main()
    # run_polling() handles its own event loop
    run()