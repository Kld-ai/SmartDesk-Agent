import asyncio
from smartdesk.agent import SmartDesk

def test_order_mock():
    out=asyncio.run(SmartDesk(mock=True).run('Where is ORD-1002?'))
    assert 'shipped' in out['answer']

def test_ticket_not_written_mock():
    out=asyncio.run(SmartDesk(mock=True).run('Create a ticket for ORD-1001'))
    assert 'awaiting' in out['answer'].lower()
