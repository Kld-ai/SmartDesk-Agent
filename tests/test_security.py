import pytest
from smartdesk.security import SecurityError,authorize,redact,save_ticket
from smartdesk.storage import get_order

def test_approval_required():
    with pytest.raises(SecurityError): authorize('create_support_ticket',False)

def test_write_blocked_without_approval():
    with pytest.raises(SecurityError): save_ticket('ORD-1001','please help',False)

def test_unknown_action_blocked():
    with pytest.raises(SecurityError): authorize('send_email',True)

def test_pii_redacted():
    assert 'sara@example.test' not in redact('sara@example.test')

def test_order_email_not_exposed():
    assert 'email' not in get_order('ORD-1001')

def test_unknown_order():
    assert get_order('ORD-9999')['error']=='order_not_found'
