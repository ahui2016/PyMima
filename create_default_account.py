import nacl.secret
import nacl.utils
import hashlib
import base64
import sys
import os
from connection import create_connection
from mimabox import MimaBox


DEFAULT_PASSWORD = "keep all secrets"


def create_default_account():
    key = hashlib.sha256(DEFAULT_PASSWORD.encode()).digest()
    secretbox = nacl.secret.SecretBox(key)
    MimaBox.secretbox = secretbox

    box = create_a_random_box()
    box.insert_into_database()


def create_a_random_box():
    """
    Let title and username be blank,
    and fill other text fields with random text.
    """
    return MimaBox(website=random_text(),
                   password=random_text(),
                   notes=random_text())


def random_text():
    text = nacl.utils.random(12)
    text = base64.b64encode(text).decode()
    return text


if __name__ == '__main__':
    pymima_db = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'pymima.db')
    if os.path.exists(pymima_db):
        print("Warning: "
              "'pymima.db' already exists, can not create new account.\n")
        sys.exit(1)
    if not create_connection():
        sys.exit(1)
    create_default_account()
