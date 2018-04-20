import nacl.secret
import nacl.utils
import hashlib
import base64
import sys

from connection import create_connection
from mimabox import MimaBox


def create_default_account():
    default_password = "keep all secrets"
    key = hashlib.sha256(default_password.encode()).digest()
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
    if not create_connection():
        sys.exit(1)
    create_default_account()
