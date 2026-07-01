import pytest

from yoak.core.agent import Agent
from yoak.core.config import Settings
from yoak.memory.canvas import clear_canvas, get_canvas, update_block
from yoak.memory.hypotheses import create_hypothesis, list_hypotheses
from yoak.memory.store import get_db


@pytest.fixture
async def db(tmp_path):
    database = await get_db(str(tmp_path / "test.db"))
    yield database
    await database.close()


@pytest.mark.asyncio
async def test_clear_canvas_empties_blocks_and_hypotheses(db):
    await update_block(db, "customer_segments", "Mango tree owners")
    await create_hypothesis(db, "customer_segments", "They will pay for pedigree analysis")

    await clear_canvas(db)

    blocks = await get_canvas(db)
    assert all(b.content == "" for b in blocks)
    assert await list_hypotheses(db) == []


@pytest.mark.asyncio
async def test_reset_chat_leaves_canvas_intact(tmp_path):
    from yoak.models.provider import Message

    settings = Settings(db_path=str(tmp_path / "yoak.db"))
    agent = Agent(settings)
    db = await agent.get_db()
    await update_block(db, "customer_segments", "Mango tree owners")
    agent._messages.append(Message(role="user", content="hello"))

    await agent.reset_chat()

    blocks = await get_canvas(db)
    assert blocks[0].content == "Mango tree owners"
    assert agent.conversation_history == []
    await agent.close()


@pytest.mark.asyncio
async def test_reset_canvas_leaves_chat_intact(tmp_path):
    from yoak.models.provider import Message

    settings = Settings(db_path=str(tmp_path / "yoak.db"))
    agent = Agent(settings)
    db = await agent.get_db()
    await update_block(db, "customer_segments", "Mango tree owners")
    agent._messages.append(Message(role="user", content="hello"))

    await agent.reset_canvas()

    blocks = await get_canvas(db)
    assert all(b.content == "" for b in blocks)
    assert len(agent.conversation_history) == 1
    await agent.close()
