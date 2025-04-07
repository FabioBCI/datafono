import imaplib
import email
import os
from pdf2image import convert_from_path
import pytesseract
import firebase_admin
from firebase_admin import credentials, firestore

# Variables del entorno (por simplicidad, puedes ponerlas aquí en la primera prueba)
GMAIL_USER = "tucorreo@gmail.com"
GMAIL_PASS = "tu_contraseña_o_token"

cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def leer_facturas():
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(GMAIL_USER, GMAIL_PASS)
    imap.select("FACTURAS")

    status, messages = imap.search(None, '(UNSEEN)')
    email_ids = messages[0].split()

    for e_id in email_ids:
        _, msg_data = imap.fetch(e_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        for part in msg.walk():
            filename = part.get_filename()
            if filename and filename.endswith('.pdf'):
                path = f"/home/tu_usuario/{filename}"
                with open(path, "wb") as f:
                    f.write(part.get_payload(decode=True))
                procesar_pdf(path)
    imap.logout()

def procesar_pdf(path):
    pages = convert_from_path(path)
    texto = ""
    for page in pages:
        texto += pytesseract.image_to_string(page)
    db.collection("facturas").add({
        "contenido": texto,
        "nombre": os.path.basename(path),
        "timestamp": firestore.SERVER_TIMESTAMP
    })

if __name__ == "__main__":
    leer_facturas()
