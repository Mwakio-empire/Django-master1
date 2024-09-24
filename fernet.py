from cryptography.fernet import Fernet

# Generate a Fernet key
key = Fernet.generate_key()
print(key.decode())  # Print the key as a string