"""Final local CSE Study247 guidance-booking voice agent used for the live demo."""

from __future__ import annotations

import os

from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.runner.types import RunnerArguments
from pipecat.services.google.gemini_live.llm import (
    GeminiLiveLLMService,
)
from pipecat.transports.base_transport import BaseTransport

from csestudy247_voice_agent.moss import make_moss_retrieval_processor
from csestudy247_voice_agent.pipeline import (
    AudioTrace,
    MetricsPrinter,
    make_transport,
    make_user_turn_params,
    require_env,
    run_pipeline,
)
from csestudy247_voice_agent.tools import GUIDANCE_SYSTEM_PROMPT, GUIDANCE_TOOLS


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    require_env("GOOGLE_API_KEY")

    llm = GeminiLiveLLMService(
        api_key=os.environ["GOOGLE_API_KEY"],
        settings=GeminiLiveLLMService.Settings(
            model=os.getenv(
                "GOOGLE_GEMINI_MODEL",
                "models/gemini-2.5-flash-native-audio-preview-12-2025",
            ),
            system_instruction=GUIDANCE_SYSTEM_PROMPT,
            voice=os.getenv("GOOGLE_GEMINI_VOICE", "Puck"),
        ),
    )

    context = LLMContext(
        tools=GUIDANCE_TOOLS,
        messages=[
            {
                "role": "user",
                "content": "A caller has just connected. Greet them warmly in one short sentence and introduce yourself as the CSE Study247 support specialist.",
            }
        ],
    )
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=make_user_turn_params(interruptions=True),
    )
    moss_retrieval = await make_moss_retrieval_processor()

    processors = [
        transport.input(),
        AudioTrace(),
        user_aggregator,
    ]
    if moss_retrieval is not None:
        processors.append(moss_retrieval)
    processors.extend(
        [
            llm,
            AudioTrace(),
            transport.output(),
            assistant_aggregator,
            MetricsPrinter(),
        ]
    )

    await run_pipeline(
        transport,
        runner_args,
        processors,
        context=context,
        metrics=True,
    )


async def bot(runner_args: RunnerArguments):
    """WebRTC bot entry point used by Pipecat's development runner."""
    transport = await make_transport(runner_args)
    await run_bot(transport, runner_args)
