from dotenv import load_dotenv
from livekit.plugins import sarvam
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
)

from livekit.plugins import groq, silero

load_dotenv()

class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            You are a helpful voice assistant.
            Keep responses short and conversational.
            """
        )

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    session = AgentSession(
        vad=silero.VAD.load(),

        stt=groq.STT(
            model="whisper-large-v3-turbo",
            language="en",
        ),

        llm=groq.LLM(
            model="llama-3.1-8b-instant",
        ),
        tts=sarvam.TTS(
                target_language_code="en-IN",
                model="bulbul:v3",
                speaker="shubh",)
    )

    # Disable audio output since no TTS is configured
   

    await session.start(
        room=ctx.room,
        agent=Assistant(),
    )

    await session.generate_reply(
        instructions="Introduce yourself briefly."
    )

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )

