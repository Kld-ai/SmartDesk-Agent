import re
from pathlib import Path
from .storage import ROOT
ALLOWED_ACTIONS = {'create_support_ticket'}
MAX_STEPS = 6
MAX_TOOL_CALLS = 8
MAX_INPUT_CHARS = 1500
MAX_OUTPUT_CHARS = 2000

class SecurityError(Exception): pass

def validate_input(message):
    if not isinstance(message,str) or not message.strip() or len(message)>MAX_INPUT_CHARS:
        raise SecurityError('Input empty or too long')
    return message

def redact(text):
    text = re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[REDACTED_EMAIL]', str(text))
    text = re.sub(r'(?i)(sk-or-v1-[a-z0-9_-]+)', '[REDACTED_KEY]', text)
    return text[:MAX_OUTPUT_CHARS]

def authorize(action, approval):
    if action not in ALLOWED_ACTIONS: raise SecurityError('Action not allowlisted')
    if approval is not True: raise SecurityError('Explicit approval required')
    return True

def save_ticket(order_id, issue, approval=False):
    authorize('create_support_ticket', approval)
    if not re.fullmatch(r'ORD-\d{4}', order_id): raise SecurityError('Invalid order ID')
    if len(issue)>500: raise SecurityError('Issue too long')
    from .storage import get_order
    if 'error' in get_order(order_id): raise SecurityError('Unknown order')
    import json, uuid
    target=ROOT/'data/tickets.jsonl'
    with target.open('a') as f:
        ticket={'ticket_id':str(uuid.uuid4()),'order_id':order_id,'issue':redact(issue)}
        f.write(json.dumps(ticket)+'\n')
    return {'status':'created','ticket_id':ticket['ticket_id']}
