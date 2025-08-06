"""
Validation Utilities - Enhanced data validation and sanitization functions for payments.
"""

import re
from typing import Optional, Tuple, Dict
from decimal import Decimal


def validate_amount(amount: float, currency: str = "USD") -> Tuple[bool, str]:
    """
    Validate payment amount with currency-specific rules.

    Args:
        amount: Amount to validate
        currency: Currency code for validation

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(amount, (int, float, Decimal)):
        return False, "Amount must be a number"

    if amount <= 0:
        return False, "Amount must be greater than 0"

    # Currency-specific minimum amounts
    min_amounts = {
        "USD": 0.50,
        "EUR": 0.50,
        "GBP": 0.30,
        "VND": 1000,
        "JPY": 50,
    }

    min_amount = min_amounts.get(currency.upper(), 0.50)
    if amount < min_amount:
        return False, f"Amount must be at least {min_amount} {currency}"

    # Maximum amount check
    max_amounts = {
        "USD": 999999.99,
        "EUR": 999999.99,
        "GBP": 999999.99,
        "VND": 999999999,
        "JPY": 9999999,
    }

    max_amount = max_amounts.get(currency.upper(), 999999.99)
    if amount > max_amount:
        return False, f"Amount exceeds maximum limit of {max_amount} {currency}"

    return True, ""


def validate_currency(currency: str) -> Tuple[bool, str]:
    """
    Validate currency code against supported currencies.

    Args:
        currency: Currency code to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not currency:
        return False, "Currency code is required"

    # Check if it's a valid 3-letter currency code
    pattern = r"^[A-Z]{3}$"
    if not re.match(pattern, currency.upper()):
        return False, "Currency code must be 3 uppercase letters"

    # List of supported currencies
    supported_currencies = {
        "USD",
        "EUR",
        "GBP",
        "VND",
        "JPY",
        "AUD",
        "CAD",
        "CHF",
        "CNY",
        "SGD",
    }

    if currency.upper() not in supported_currencies:
        return False, f"Currency {currency} is not supported"

    return True, ""


def validate_payment_method(payment_method: str) -> Tuple[bool, str]:
    """
    Validate payment method.

    Args:
        payment_method: Payment method to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not payment_method:
        return False, "Payment method is required"

    supported_methods = {"stripe", "momo", "vnpay", "paypal", "apple_pay", "google_pay"}

    if payment_method.lower() not in supported_methods:
        return False, f"Payment method '{payment_method}' is not supported"

    return True, ""


def validate_payment_method_currency_combination(
    payment_method: str, currency: str
) -> Tuple[bool, str]:
    """
    Validate payment method and currency combination.

    Args:
        payment_method: Payment method
        currency: Currency code

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Payment method specific currency support
    method_currency_support = {
        "stripe": {"USD", "EUR", "GBP", "AUD", "CAD", "CHF", "JPY", "SGD"},
        "momo": {"VND"},
        "vnpay": {"VND"},
        "paypal": {"USD", "EUR", "GBP", "AUD", "CAD", "JPY"},
        "apple_pay": {"USD", "EUR", "GBP", "AUD", "CAD", "CHF", "JPY", "SGD"},
        "google_pay": {"USD", "EUR", "GBP", "AUD", "CAD", "CHF", "JPY", "SGD"},
    }

    supported_currencies = method_currency_support.get(payment_method.lower())
    if not supported_currencies:
        return False, f"Unknown payment method: {payment_method}"

    if currency.upper() not in supported_currencies:
        return (
            False,
            f"Payment method '{payment_method}' does not support currency '{currency}'",
        )

    return True, ""
    """
    Validate payment method.

    Args:
        payment_method: Payment method to validate

    Returns:
        True if valid, False otherwise
    """
    valid_methods = ["stripe", "momo", "vnpay"]
    return payment_method.lower() in valid_methods


def validate_payment_intent_id(payment_intent_id: str) -> bool:
    """
    Validate payment intent ID format.

    Args:
        payment_intent_id: Payment intent ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not payment_intent_id:
        return False

    # Check if it's a valid format (alphanumeric with possible hyphens/underscores)
    pattern = r"^[a-zA-Z0-9_-]+$"
    return re.match(pattern, payment_intent_id) is not None


def validate_promotion_code(promotion_code: str) -> bool:
    """
    Validate promotion code format.

    Args:
        promotion_code: Promotion code to validate

    Returns:
        True if valid, False otherwise
    """
    if not promotion_code:
        return False

    # Promotion codes should be alphanumeric with possible hyphens
    pattern = r"^[a-zA-Z0-9-]+$"
    return re.match(pattern, promotion_code) is not None


def validate_order_id(order_id: str) -> bool:
    """
    Validate order ID format.

    Args:
        order_id: Order ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not order_id:
        return False

    # Order IDs should be alphanumeric with possible hyphens/underscores
    pattern = r"^[a-zA-Z0-9_-]+$"
    return re.match(pattern, order_id) is not None


def sanitize_string(input_str: str) -> str:
    """
    Sanitize string input.

    Args:
        input_str: Input string to sanitize

    Returns:
        Sanitized string
    """
    if not input_str:
        return ""

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', "", input_str)
    return sanitized.strip()


def format_amount(amount: float, currency: str = "USD") -> str:
    """
    Format amount with currency.

    Args:
        amount: Amount to format
        currency: Currency code

    Returns:
        Formatted amount string
    """
    try:
        decimal_amount = Decimal(str(amount))
        return f"{decimal_amount:.2f} {currency}"
    except (ValueError, TypeError):
        return f"{amount} {currency}"


def validate_webhook_signature(signature: str, payload: str, secret: str) -> bool:
    """
    Validate webhook signature.

    Args:
        signature: Webhook signature
        payload: Webhook payload
        secret: Webhook secret

    Returns:
        True if valid, False otherwise
    """
    # This is a placeholder implementation
    # In a real application, you would implement proper signature validation
    # based on the specific payment gateway's requirements

    if not signature or not payload or not secret:
        return False

    # Add your signature validation logic here
    # Example for Stripe:
    # import hmac
    # import hashlib
    # expected_signature = hmac.new(
    #     secret.encode('utf-8'),
    #     payload.encode('utf-8'),
    #     hashlib.sha256
    # ).hexdigest()
    # return hmac.compare_digest(signature, expected_signature)

    return True


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    if not phone:
        return False

    # Remove all non-digit characters
    digits_only = re.sub(r"\D", "", phone)

    # Check if it's a valid length (10-15 digits)
    if len(digits_only) < 10 or len(digits_only) > 15:
        return False

    return True


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email string to validate

    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def calculate_discount_amount(
    original_amount: float, discount_percentage: float
) -> float:
    """
    Calculate discount amount.

    Args:
        original_amount: Original amount
        discount_percentage: Discount percentage (0-100)

    Returns:
        Discount amount
    """
    if discount_percentage < 0 or discount_percentage > 100:
        return 0.0

    return original_amount * (discount_percentage / 100)


def calculate_final_amount(original_amount: float, discount_amount: float) -> float:
    """
    Calculate final amount after discount.

    Args:
        original_amount: Original amount
        discount_amount: Discount amount

    Returns:
        Final amount
    """
    final_amount = original_amount - discount_amount
    return max(0.0, final_amount)
