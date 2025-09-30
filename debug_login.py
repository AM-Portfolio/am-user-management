#!/usr/bin/env python3
"""Debug login password verification"""
import bcrypt

# Test password that we know was used
test_password = "testpassword123"
stored_hash = "$2b$12$.kUCJz67SToyd3enkn9v.e/F3wysg6yZWtK3C6WLHYsFJO24GMmrS"

# Test bcrypt verification
print(f"Testing password: {test_password}")
print(f"Stored hash: {stored_hash}")

try:
    is_valid = bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8'))
    print(f"Password verification result: {is_valid}")
except Exception as e:
    print(f"Error during verification: {e}")

# Let's also create a fresh hash with the same password and see if it matches
fresh_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt(rounds=12))
print(f"Fresh hash: {fresh_hash.decode('utf-8')}")

# Try verifying with fresh hash
try:
    fresh_is_valid = bcrypt.checkpw(test_password.encode('utf-8'), fresh_hash)
    print(f"Fresh hash verification: {fresh_is_valid}")
except Exception as e:
    print(f"Error with fresh hash: {e}")