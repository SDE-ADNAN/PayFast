import re
from src.upi.services import validate_vpa_format, generate_default_vpa

def test_vpa_validation() -> None:
    assert validate_vpa_format("alice@payfast") is True
    assert validate_vpa_format("john.doe_123@payfast") is True
    assert validate_vpa_format("aa@payfast") is False # Too short
    assert validate_vpa_format("invalid!vpa@payfast") is False

def test_generate_default_vpa() -> None:
    assert generate_default_vpa("+919876543210", "John Doe") == "john.doe@payfast"
    assert generate_default_vpa("+919876543210", "J") == "+919876543210@payfast"
