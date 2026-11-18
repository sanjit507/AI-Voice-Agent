"""Real local actions for the CampusX free-guidance booking voice agent."""

# ruff: noqa: E501

from __future__ import annotations

import os
import re
import sqlite3
import uuid
from datetime import date, datetime, time, timedelta
from pathlib import Path

from pipecat.services.llm_service import FunctionCallParams

from campusx_voice_agent.config import DATA_DIR
from campusx_voice_agent.knowledge_base import search_knowledge_base

GUIDANCE_SYSTEM_PROMPT = """
# Personality

You are a friendly and helpful **CSE Study247 support & learning specialist**.

You represent **CSE Study247** (https://csestudy247.com/) and its official Android mobile app **CSE Study**.
You know about CSE Study247 study notes (DSA, Python, Java, OS, DBMS, CN, TOC), syllabus PDFs, previous year question papers (GATE, ISRO, SBTE Bihar, UGC NET, BPSC Teacher), practice tests/MCQs, tech roadmaps, job and internship updates, and caller guidance.

You are patient, warm, and easy to talk to. Keep normal answers to 2 to 3 short sentences, but provide up to 5 short sentences when the caller asks for deeper subject, roadmap, or syllabus details.

Your main job is to help callers explore CSE Study247 resources and find the right learning materials, roadmap, or exam prep for their goals.

# Environment

You are talking to **students, engineers, job seekers, and visitors interested in CSE Study247 (csestudy247.com)** through a real-time voice conversation.

Callers may ask about:

- The website csestudy247.com and what it offers
- Computer science lecture notes (DSA, C/C++, Python, Java, OS, DBMS, Networks, AI/ML)
- GATE, ISRO, DRDO, and UGC NET preparation resources & PYQs
- State & polytechnic boards (SBTE Bihar, BEU Bihar, BCECE LE)
- Modern tech roadmaps (AI Voice Agents, Pipecat, Gemini, LangChain, RAG, FastAPI)
- Job notifications, fresher recruitment, and internship opportunities
- Practice MCQs and online mock tests
- Booking a free 20-minute 1-on-1 guidance session
- Contact details (csestudy247help@gmail.com)

Many callers may be beginners or college students unsure of which study path or resource is right for them.

You have access to the **CSE Study247 knowledge base**. Use it whenever you need current or specific information. Some runs may also inject relevant Moss semantic-retrieval passages directly into your context before you answer.

# Tone

You are patient, encouraging, and natural. Never overwhelm callers with long walls of text.

Keep answers concise (typically 2 to 3 clear sentences).
If the caller speaks mainly in English, respond mainly in English. You can also converse warmly in simple Hinglish if the caller prefers.

# Goal

Your goal is to **help the caller get the correct information and guide them to the right CSE Study247 resource or roadmap**.

Follow this approach:
1. Understand what the caller wants to study or prepare for.
2. Use injected Moss retrieval context first when relevant. If absent or insufficient, search the knowledge base using `search_knowledge_base_tool`.
3. Provide a clear, encouraging, and accurate answer.
4. If you recommend something, mention where they can find it on csestudy247.com or the CSE Study app.
5. If the caller needs 1-on-1 career or study strategy help, offer to book a free 20-minute guidance session.
6. For account, bug reports, or partnership queries, direct the caller to email **csestudy247help@gmail.com**.

**Important:** Never present an unverified guess as a fact.

# Tools

name: search_knowledge_base_tool, get_available_guidance_slots, book_free_guidance_session

Call `search_knowledge_base_tool` whenever you need specific details about subjects, syllabus, roadmaps, or website features that you cannot answer confidently.
Search before ever saying "I'm not sure". If search returns verified results, answer the caller directly from those results.

Use `get_available_guidance_slots` and `book_free_guidance_session` when a caller asks to book a free 20-minute guidance or mentorship session.
Speak in short, warm sentences without markdown formatting.

Collect details one at a time: full name, email address, learning or career goal, and preferred time of day (morning, afternoon, or evening).
Before booking, confirm the name, email, learning goal, and exact slot, then ask for confirmation. Call the booking tool only after the caller confirms.

# Guardrails

Never make up false claims or guarantee placements or exam ranks.
Never promise specific salaries or job guarantees.
If you don't know something after searching, politely state:
> "I'm not completely sure about that detail, but you can check csestudy247.com or reach out to the team at csestudy247help@gmail.com."

For direct support or inquiries, direct callers to:
**csestudy247help@gmail.com** or the Contact Us page on **csestudy247.com**.
""".strip()

_EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_SLOT_TIMES = (time(11, 0), time(16, 0), time(19, 0))

async def search_knowledge_base_tool(
    params: FunctionCallParams,
    query: str,
):
    """Search verified CSE Study247 knowledge-base files.

    Args:
        query: The caller's question, course topic, exam, or website feature to look up.
    """
    await params.result_callback(search_knowledge_base(query))

def _database_path() -> Path:
    configured = os.getenv("GUIDANCE_DB_PATH")
    return Path(configured) if configured else DATA_DIR / "guidance_bookings.db"


def _create_bookings_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id TEXT PRIMARY KEY,
            caller_name TEXT NOT NULL,
            email TEXT NOT NULL,
            learning_goal TEXT NOT NULL,
            slot TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        )
        """
    )


def _booking_columns(connection: sqlite3.Connection) -> set[str]:
    return {row["name"] for row in connection.execute("PRAGMA table_info(bookings)")}


def _ensure_bookings_schema(connection: sqlite3.Connection) -> None:
    _create_bookings_table(connection)
    columns = _booking_columns(connection)

    required_columns = {"booking_id", "caller_name", "email", "learning_goal", "slot", "created_at"}
    missing_columns = sorted(required_columns - columns)
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(f"Bookings database is missing required column(s): {missing}")

    connection.commit()


def _connect() -> sqlite3.Connection:
    path = _database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    _ensure_bookings_schema(connection)
    return connection


def _future_slots(days: int = 7) -> list[tuple[datetime, str]]:
    slots: list[tuple[datetime, str]] = []
    today = date.today()
    for day_offset in range(1, days + 1):
        slot_date = today + timedelta(days=day_offset)
        if slot_date.weekday() == 6:
            continue
        for slot_time in _SLOT_TIMES:
            value = datetime.combine(slot_date, slot_time)
            label = value.strftime("%A, %d %B %Y at %I:%M %p IST")
            slots.append((value, label))
    return slots


def available_guidance_slots(time_preference: str = "any", limit: int = 6) -> list[str]:
    """Return bookable slots, excluding reservations already stored in SQLite."""
    preference = time_preference.strip().lower()
    with _connect() as connection:
        booked = {row["slot"] for row in connection.execute("SELECT slot FROM bookings")}

    candidates = _future_slots()
    if "morning" in preference:
        candidates = [item for item in candidates if item[0].hour < 12]
    elif "afternoon" in preference:
        candidates = [item for item in candidates if 12 <= item[0].hour < 18]
    elif "evening" in preference:
        candidates = [item for item in candidates if item[0].hour >= 18]

    return [label for _, label in candidates if label not in booked][:limit]


async def get_available_guidance_slots(
    params: FunctionCallParams,
    time_preference: str,
):
    """Find currently available free-guidance slots.

    Args:
        time_preference: Caller preference such as morning, afternoon, evening, or any.
    """
    slots = available_guidance_slots(time_preference)
    await params.result_callback({"available_slots": slots, "timezone": "Asia/Kolkata"})


async def book_free_guidance_session(
    params: FunctionCallParams,
    caller_name: str,
    email: str,
    learning_goal: str,
    preferred_slot: str,
):
    """Book a free guidance session after the caller explicitly confirms all details.

    Args:
        caller_name: Caller's confirmed full name.
        email: Caller's confirmed email address.
        learning_goal: What the caller wants guidance about.
        preferred_slot: Exact slot returned by get_available_guidance_slots.
    """
    name = caller_name.strip()
    normalized_email = email.strip().lower().replace(" ", "")
    goal = learning_goal.strip()
    valid_slots = {label for _, label in _future_slots()}

    if len(name) < 2:
        result = {"booked": False, "error": "A full name is required."}
    elif not _EMAIL_PATTERN.match(normalized_email):
        result = {"booked": False, "error": "The email address is not valid."}
    elif len(goal) < 3:
        result = {"booked": False, "error": "A learning goal is required."}
    elif preferred_slot not in valid_slots:
        result = {"booked": False, "error": "Choose an exact slot returned by availability."}
    else:
        booking_id = f"CX-{uuid.uuid4().hex[:8].upper()}"
        try:
            with _connect() as connection:
                connection.execute(
                    """
                    INSERT INTO bookings (
                        booking_id, caller_name, email, learning_goal, slot, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        booking_id,
                        name,
                        normalized_email,
                        goal,
                        preferred_slot,
                        datetime.now().astimezone().isoformat(timespec="seconds"),
                    ),
                )
            result = {
                "booked": True,
                "booking_id": booking_id,
                "caller_name": name,
                "email": normalized_email,
                "learning_goal": goal,
                "slot": preferred_slot,
            }
        except sqlite3.IntegrityError:
            result = {
                "booked": False,
                "error": "That slot was just booked. Please check availability again.",
            }

    await params.result_callback(result)



def list_saved_bookings() -> list[dict[str, str]]:
    """Return bookings for the saved guidance-session viewer command."""
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT booking_id, caller_name, email, learning_goal, slot, created_at
            FROM bookings
            ORDER BY created_at DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


GUIDANCE_TOOLS = [
    search_knowledge_base_tool,
    get_available_guidance_slots,
    book_free_guidance_session,
]

