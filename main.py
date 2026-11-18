"""Single entry point for the CampusX local voice-agent codebase."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parent
SRC_DIR = PROJECT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from campusx_voice_agent import config as _config  # noqa: E402,F401
from campusx_voice_agent.bookings import show_bookings  # noqa: E402
from campusx_voice_agent.moss_index import main as create_moss_index  # noqa: E402


async def bot(runner_args: Any):
    from campusx_voice_agent.agent import bot as voice_agent_bot

    await voice_agent_bot(runner_args)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "bookings":
        show_bookings()
        return

    if len(sys.argv) > 1 and sys.argv[1] in {"moss-index", "create-moss-index"}:
        create_moss_index()
        return

    from pipecat.runner.run import main as pipecat_main

    pipecat_main()


if __name__ == "__main__":
    main()