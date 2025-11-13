import os
import imaplib
from typing import List, Tuple


class ImapConfigError(RuntimeError):
    pass


def get_imap_config() -> Tuple[str, int, str, str, str]:
    """Read IMAP config from environment.

    Required:
      IMAP_HOST
      IMAP_USER
      IMAP_PASSWORD

    Optional:
      IMAP_PORT (default 993)
      IMAP_FOLDER (default "INBOX")
    """
    host = os.getenv("IMAP_HOST")
    user = os.getenv("IMAP_USER")
    password = os.getenv("IMAP_PASSWORD")
    port = int(os.getenv("IMAP_PORT", "993"))
    folder = os.getenv("IMAP_FOLDER", "INBOX")

    if not host or not user or not password:
        raise ImapConfigError("IMAP_HOST, IMAP_USER, IMAP_PASSWORD must be set")

    return host, port, user, password, folder


def fetch_unseen_emails() -> List[bytes]:
    """Connect to IMAP and fetch UNSEEN messages (RFC822 bytes).

    This is not used in unit tests (they operate on .eml files),
    but can be used in production.
    """
    host, port, user, password, folder = get_imap_config()

    mail = imaplib.IMAP4_SSL(host, port)
    mail.login(user, password)
    mail.select(folder)

    typ, data = mail.search(None, "UNSEEN")
    if typ != "OK":
        mail.logout()
        return []

    ids = data[0].split()
    messages: List[bytes] = []
    for msg_id in ids:
        typ, msg_data = mail.fetch(msg_id, "(RFC822)")
        if typ != "OK":
            continue
        for part in msg_data:
            if isinstance(part, tuple):
                messages.append(part[1])

    mail.logout()
    return messages
