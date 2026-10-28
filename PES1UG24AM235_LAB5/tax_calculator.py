
"""Income tax calculator with PAN encryption and Form 16 parsing."""

import os
import re

from defusedxml import minidom
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Slabs configured for this program (modelled on FY 2025-26).
STANDARD_DEDUCTION_NEW = 75000
STANDARD_DEDUCTION_OLD = 50000
REBATE_LIMIT_NEW = 1200000
CESS = 0.04
OLD_SLABS = [
    (250000, 0.0),
    (500000, 0.05),
    (1000000, 0.20),
    (float("inf"), 0.30),
]


def slab_rate(income):
    """Return the new-regime slab rate for taxable income."""
    if income <= 400000:
        return 0.0
    if income <= 800000:
        return 0.05
    if income <= 1200000:
        return 0.10
    if income <= 1600000:
        return 0.15
    if income <= 2000000:
        return 0.20
    if income <= 2400000:
        return 0.25
    return 0.30


def new_regime_tax(salary):
    """Calculate tax under the new regime."""
    taxable = max(0, salary - STANDARD_DEDUCTION_NEW)
    tax_rate = slab_rate(taxable)
    tax_amount = taxable * tax_rate

    if taxable < REBATE_LIMIT_NEW:
        tax_amount = 0

    return int(tax_amount * (1 + CESS))


def basic_exemption(age):
    """Return the basic exemption limit for the taxpayer's age."""
    if age >= 80:
        return 500000
    if age >= 60:
        return 300000
    return 250000


def old_regime_tax(salary, age, deductions):
    """Calculate old-regime tax after eligible deductions."""
    taxable = max(0, salary - STANDARD_DEDUCTION_OLD)
    taxable -= sum(deductions.values())

    total_tax = 0.0
    lower_limit = basic_exemption(age)

    for upper_limit, rate in OLD_SLABS:
        if taxable > lower_limit and rate > 0:
            taxable_in_slab = min(taxable, upper_limit) - lower_limit
            total_tax += taxable_in_slab * rate
        lower_limit = max(lower_limit, upper_limit)

    return int(total_tax * (1 + CESS))


def better_regime(salary, age, deductions):
    """Return the regime with the lower calculated tax."""
    new_tax = new_regime_tax(salary)
    old_tax = old_regime_tax(salary, age, deductions)

    if new_tax <= old_tax:
        return "new"
    return "old"


def is_valid_pan(pan):
    """Check whether a PAN matches the expected format."""
    return bool(re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan))


def encrypt_pan(pan):
    """Encrypt a PAN with AES-GCM using an environment-provided key."""
    key_hex = os.environ.get("PAN_ENCRYPTION_KEY")
    if key_hex is None:
        raise ValueError("PAN_ENCRYPTION_KEY environment variable is required")

    try:
        key = bytes.fromhex(key_hex)
    except ValueError as exc:
        raise ValueError(
            "PAN_ENCRYPTION_KEY must be hexadecimal"
        ) from exc

    if len(key) not in (16, 24, 32):
        raise ValueError("AES key must contain 16, 24, or 32 bytes")

    nonce = os.urandom(12)
    ciphertext = AESGCM(key).encrypt(
        nonce,
        pan.encode("utf-8"),
        None,
    )
    return (nonce + ciphertext).hex()


def signing_key():
    """Generate a 2048-bit RSA private key."""
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )


def parse_form16(xml_text, strict=True):
    """Extract salary and TDS amounts from Form 16 XML."""
    del strict  # Retained for compatibility with the original function API.
    doc = minidom.parseString(xml_text)
    salary_text = doc.getElementsByTagName("salary")[0].firstChild.data
    tds_text = doc.getElementsByTagName("tds")[0].firstChild.data
    return int(salary_text), int(tds_text)


def main():
    """Run sample calculations and security checks."""
    print(f"New regime, salary 12,75,000: {new_regime_tax(1275000)}")
    print(f"New regime, salary 18,00,000: {new_regime_tax(1800000)}")

    deductions = {"80C": 200000, "80D": 30000}
    print(
        "Old regime, salary 18,00,000: "
        f"{old_regime_tax(1800000, 35, deductions)}"
    )
    print(
        "Better regime: "
        f"{better_regime(1800000, 35, deductions)}"
    )
    print(f"Basic exemption at age 80: {basic_exemption(80)}")
    print(f"PAN 'ABCDE1234F' valid? {is_valid_pan('ABCDE1234F')}")

    encrypted_first = encrypt_pan("ABCDE1234F")
    encrypted_second = encrypt_pan("ABCDE1234F")
    print(
        "Same PAN encrypts the same way twice? "
        f"{encrypted_first == encrypted_second}"
    )

    sample_xml = (
        "<form16><salary>1800000</salary>"
        "<tds>150000</tds></form16>"
    )
    print(f"Form 16: {parse_form16(sample_xml)}")
    print(f"Signing key size: {signing_key().key_size}")


if __name__ == "__main__":
    main()
