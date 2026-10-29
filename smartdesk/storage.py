import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def orders():
    return json.loads((ROOT/'data/orders.json').read_text())

def get_order(order_id):
    for order in orders():
        if order['order_id'] == order_id:
            return {k:v for k,v in order.items() if k != 'email'}
    return {'error':'order_not_found'}

def policy(topic):
    text = (ROOT/'data/policy.txt').read_text()
    lines = [s for s in text.splitlines() if topic.lower() in s.lower()]
    return '\n'.join(lines) if lines else text
