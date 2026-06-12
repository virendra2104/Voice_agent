import os
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.plugins import elevenlabs, groq, silero
print("ELEVEN:", repr(os.getenv("ELEVENLABS_API_KEY")))
print("GROQ:", repr(os.getenv("GROQ_API_KEY")))
# 1. Load the environment variables from your .env file
load_dotenv()

class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            You are Mona voice assistant
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
        
        # 2. Configured exactly to bridge your doc info with LiveKit's streaming architecture
        tts=elevenlabs.TTS(
            api_key=os.getenv("ELEVENLABS_API_KEY"), # Uses the exact key from your doc snippet
            voice_id="JBFqnCBsd6RMkjVDRZzb",         # Uses "George" from your doc snippet
            model="eleven_multilingual_v2",               # CRITICAL: Must use turbo_v2 or flash_v1 for streaming websocket audio
        )
    )

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
