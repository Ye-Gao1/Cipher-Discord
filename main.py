import discord
from discord import app_commands
import random, os
import yaml
TOKEN = os.environ["TOKEN"]

characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 !@#$%^&*()-_+=`~;:'[]{}|<>,./?\"\\"
character_count = len(characters)

saved_keys = {}
yaml_file = "./cipher-ui/public/encrypted_messages.yaml"

if os.path.exists(yaml_file):
    with open(yaml_file, "r") as file:
        encrypted_messages = yaml.safe_load(file) or {}
else:
    encrypted_messages = {}

def adjust_key_length(key, message):
    return (key * (len(message) // len(key)) + key[:len(message) % len(key)]) if key else ""

def encrypt_character(plain, key):
    key_code = characters.index(key)
    plain_code = characters.index(plain)
    cipher_code = (key_code + plain_code) % character_count
    cipher = characters[cipher_code]
    return cipher

def encrypt(plain, key):
    cipher = ""
    for (plain_index, plain_character) in enumerate(plain):
        key_index = plain_index % len(key)
        key_character = key[key_index]
        cipher_character = encrypt_character(plain_character, key_character)
        cipher += cipher_character
    return cipher

def decrypt_character(cipher, key):
    key_code = characters.index(key)
    cipher_code = characters.index(cipher)
    plain_code = (cipher_code - key_code) % character_count
    plain = characters[plain_code]
    return plain

def decrypt(cipher, key):
    plain = ""
    for (cipher_index, cipher_character) in enumerate(cipher):
        key_index = cipher_index % len(key)
        key_character = key[key_index]
        plain_character = decrypt_character(cipher_character, key_character)
        plain += plain_character
    return plain

def random_key(length):
    return ''.join(random.choice(characters) for _ in range(length))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

@tree.command(name="encrypt", description="Encrypt a message using a key.")
async def encrypt_message(interaction: discord.Interaction, message: str, key: str):
    adjusted_key = adjust_key_length(key, message)
    encrypted_message = encrypt(message, adjusted_key)

    user_id = str(interaction.user.id)
    if user_id not in encrypted_messages:
        encrypted_messages[user_id] = []

    encrypted_messages[user_id].append({"message": message, "encrypted": encrypted_message, "key": key})

    with open(yaml_file, "w") as file:
        yaml.dump(encrypted_messages, file)

    await interaction.response.send_message(f"Encrypted message: {encrypted_message}")

@tree.command(name="decrypt", description="Decrypt a message using a key.")
async def decrypt_message(interaction: discord.Interaction, encrypted_message: str, key: str):
    adjusted_key = adjust_key_length(key, encrypted_message)
    decrypted_message = decrypt(encrypted_message, adjusted_key)
    await interaction.response.send_message(f"Decrypted message: {decrypted_message}")

client.run(TOKEN)
