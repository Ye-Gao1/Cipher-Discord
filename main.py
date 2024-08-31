import discord
from discord import app_commands
import random, os
import yaml
TOKEN = os.environ["TOKEN"]

characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 !@#$%^&*()-_+=`~;:'[]{}|<>,./?\"\\"
character_count = len(characters)
yaml_file = "./cipher-ui/public/encrypted_messages.yaml"

def load_yaml():
    if os.path.exists(yaml_file):
        with open(yaml_file, "r") as file:
            return yaml.safe_load(file) or {}
    return {}

def save_yaml(data):
    with open(yaml_file, "w") as file:
        yaml.dump(data, file)

data = load_yaml()

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

def invert_character(character):
    character_code = characters.index(character)
    inverted_code = (character_count - character_code) % character_count
    inverted_character = characters[inverted_code]
    return inverted_character

def invert(text):
    inverted_text = ""
    for character in text:
        inverted_text += invert_character(character)
    return inverted_text

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
    if user_id not in data:
        data[user_id] = {"messages": [], "keys": {}}
    elif isinstance(data[user_id], list):
        data[user_id] = {"messages": data[user_id], "keys": {}}

    data[user_id]["messages"].append({"message": message, "encrypted": encrypted_message, "key": key})
    save_yaml(data)

    await interaction.response.send_message(f"Encrypted message: {encrypted_message}")

@tree.command(name="decrypt", description="Decrypt a message using a key.")
async def decrypt_message(interaction: discord.Interaction, encrypted_message: str, key: str):
    adjusted_key = adjust_key_length(key, encrypted_message)
    decrypted_message = decrypt(encrypted_message, adjusted_key)
    await interaction.response.send_message(f"Decrypted message: {decrypted_message}")

@tree.command(name="generate_key", description="Generate a random key of a given length.")
async def generate_key(interaction: discord.Interaction, length: int):
    key = random_key(length)
    await interaction.response.send_message(f"Generated key: {key}")

@tree.command(name="save_key", description="Save a key with a name for later use.")
async def save_key(interaction: discord.Interaction, key: str, name: str):
    user_id = str(interaction.user.id)
    if user_id not in data:
        data[user_id] = {"messages": [], "keys": {}}
    elif isinstance(data[user_id], list):
        data[user_id] = {"messages": data[user_id], "keys": {}}

    data[user_id]["keys"][name] = key
    save_yaml(data)
    await interaction.response.send_message(f"Key '{name}' saved.")

@tree.command(name="retrieve_key", description="Retrieve a saved key by its name.")
async def retrieve_key(interaction: discord.Interaction, name: str):
    user_id = str(interaction.user.id)
    user_data = data.get(user_id, {})
    if isinstance(user_data, list):
        user_data = {"messages": user_data, "keys": {}}
    key = user_data.get("keys", {}).get(name)
    if key:
        await interaction.response.send_message(f"Key '{name}': {key}")
    else:
        await interaction.response.send_message(f"No key found with the name '{name}'.")

@tree.command(name="list_keys", description="List all saved keys.")
async def list_keys(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_data = data.get(user_id, {})
    if isinstance(user_data, list):
        user_data = {"messages": user_data, "keys": {}}
    user_keys = user_data.get("keys", {})
    if user_keys:
        keys_list = "\n".join([f"{name}: {key}" for name, key in user_keys.items()])
        await interaction.response.send_message(f"Saved keys:\n{keys_list}")
    else:
        await interaction.response.send_message("No keys have been saved yet.")

@tree.command(name="delete_key", description="Delete a saved key by its name.")
async def delete_key(interaction: discord.Interaction, name: str):
    user_id = str(interaction.user.id)
    user_data = data.get(user_id, {})
    if isinstance(user_data, list):
        user_data = {"messages": user_data, "keys": {}}
    user_keys = user_data.get("keys", {})
    if name in user_keys:
        del user_keys[name]
        save_yaml(data)
        await interaction.response.send_message(f"Key '{name}' deleted.")
    else:
        await interaction.response.send_message(f"No key found with the name '{name}'.")

@tree.command(name="invert", description="Invert the characters of a message.")
async def invert_message(interaction: discord.Interaction, message: str):
    inverted_message = invert(message)
    await interaction.response.send_message(f"Inverted message: {inverted_message}")

@tree.command(name="list_messages", description="List all encrypted messages for the user.")
async def list_messages(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_data = data.get(user_id, {})
    if isinstance(user_data, list):
        user_messages = user_data
    else:
        user_messages = user_data.get("messages", [])
    
    if user_messages:
        message_list = "\n".join([f"Message: {msg['message']}, Encrypted: {msg['encrypted']}, Key: {msg['key']}" for msg in user_messages])
        await interaction.response.send_message(f"Your encrypted messages:\n{message_list}")
    else:
        await interaction.response.send_message("You don't have any encrypted messages.")
        
client.run(TOKEN)