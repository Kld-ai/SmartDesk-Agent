"""SmartDesk CLI: single question or interactive session with human approval."""
import argparse
import asyncio
import json
from dotenv import load_dotenv
from .agent import SmartDesk
from .security import SecurityError, save_ticket


def request_human_approval(order_id, issue):
    print('\n' + '=' * 45)
    print('HUMAN APPROVAL REQUIRED')
    print('=' * 45)
    print(f'Order: {order_id}')
    print(f'Issue: {issue}')
    try:
        choice = input('Approve ticket creation? (yes/no): ').strip().lower()
    except (EOFError, KeyboardInterrupt):
        choice = 'no'
    if choice != 'yes':
        print('Ticket rejected. No write performed.')
        return {'status': 'rejected', 'write_performed': False}
    try:
        result = save_ticket(order_id, issue, approval=True)
        print('Ticket successfully created! Ticket ID:', result['ticket_id'])
        return result
    except SecurityError as exc:
        print('Security error:', exc)
        return {'status': 'error', 'write_performed': False}


async def ask(agent, question):
    result = await agent.run(question)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if agent.pending_ticket:
        ticket = agent.pending_ticket
        approval = request_human_approval(ticket['order_id'], ticket['issue'])
        print('Approval Result:', json.dumps(approval, indent=2, ensure_ascii=False))


async def interactive(agent):
    print('SmartDesk interactive session. Type /exit to quit, /reset for a new session.')
    while True:
        try:
            question = input('\nYou: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nGoodbye!')
            break
        if question.lower() in {'/exit', '/quit'}:
            break
        if question.lower() == '/reset':
            agent.messages = agent.messages[:1]
            agent.pending_ticket = None
            print('Session memory cleared.')
            continue
        if not question:
            continue
        try:
            await ask(agent, question)
        except (SecurityError, ValueError) as exc:
            print('Error:', exc)


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description='SmartDesk Agent CLI')
    parser.add_argument('--mock', action='store_true')
    parser.add_argument('--question', default='What is the status of ORD-1001?')
    parser.add_argument('--config', choices=['A', 'B'], default='B')
    parser.add_argument('--chat', action='store_true', help='Interactive session with memory')
    parser.add_argument('--approve-ticket', nargs=2, metavar=('ORDER_ID', 'ISSUE'))
    args = parser.parse_args()
    if args.approve_ticket:
        request_human_approval(*args.approve_ticket)
        return
    agent = SmartDesk(mock=args.mock, config=args.config)
    asyncio.run(interactive(agent) if args.chat else ask(agent, args.question))


if __name__ == '__main__':
    main()
