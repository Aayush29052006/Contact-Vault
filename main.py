"""ContactVault entry point.

No arguments -> launches the GUI. Any arguments -> dispatches to the CLI.
"""

import sys


def main() -> int:
    if len(sys.argv) > 1:
        from contactvault.cli.cli import main as cli_main
        return cli_main(sys.argv[1:])

    from contactvault.gui.app import run
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main())