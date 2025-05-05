import pytest
import re
import uuid
from prometheus_swarm.utils.transaction_cleanup import clean_transaction_id

def test_clean_transaction_id_basic():
    # Test basic string input
    result = clean_transaction_id("test-transaction-123")
    assert result == "testtransaction123"
    assert len(result) <= 36

def test_clean_transaction_id_none():
    # Test None input generates a valid UUID
    result = clean_transaction_id(None)
    assert re.match(r'^[0-9a-f-]+$', result)
    assert len(result) == 36

def test_clean_transaction_id_integer():
    # Test integer input
    result = clean_transaction_id(12345)
    assert result == "12345"

def test_clean_transaction_id_special_chars():
    # Test input with special characters
    result = clean_transaction_id("!@#test-transaction$%^&*")
    assert result == "testtransaction"

def test_clean_transaction_id_empty_string():
    # Test empty string input
    result = clean_transaction_id("")
    assert re.match(r'^[0-9a-f-]+$', result)
    assert len(result) == 36

def test_clean_transaction_id_long_input():
    # Test very long input is truncated
    long_id = "x" * 100
    result = clean_transaction_id(long_id)
    assert len(result) <= 36
    assert result.startswith("x" * 36)

def test_clean_transaction_id_case_sensitivity():
    # Test case conversion
    result = clean_transaction_id("TEST-Transaction-123")
    assert result == "testtransaction123"

def test_clean_transaction_id_unicode():
    # Test unicode input
    result = clean_transaction_id("тестовый-транзакция")
    assert result == "тестовыйтранзакция"

@pytest.mark.parametrize("input_val", [
    None, 
    "", 
    "   ", 
    object(), 
    Exception()
])
def test_clean_transaction_id_fallback(input_val):
    # Test various problematic inputs fall back to UUID
    result = clean_transaction_id(input_val)
    assert re.match(r'^[0-9a-f-]+$', result)
    assert len(result) == 36