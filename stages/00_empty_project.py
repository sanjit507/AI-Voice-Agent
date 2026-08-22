"""Stage 00: prove the project and virtual environment are ready.

This file intentionally does not build a voice pipeline. It gives users a
small first checkpoint: Python can import Pipecat, so the environment is ready
for the transport stage that follows.
"""

# Stage 00 introduces only one dependency check: can this Python environment
# import Pipecat at all? If this line fails, the virtual environment or package
# installation is not ready, and later pipeline code will fail too.
import pipecat

# Print a plain success message first so users can immediately see that the
# script reached runtime after the import completed.
print("Pipecat imported successfully.")

# Show the imported package name from the module object. This makes the check a
# little more concrete than a silent import by showing what Python loaded.
print(f"Loaded package: {pipecat.__name__}")

# This stage deliberately exposes the missing capability. The project is alive,
# but there is still no microphone, transport, STT, LLM, or TTS in the pipeline.
