import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging
import keyring

logging.basicConfig(level=logging.DEBUG, filename="envoi_email_log.txt", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")


class EnvoiGMail:
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    def __init__(self, username, password=None):
        self.username = username
        self.password = self.password_init(password)
        self.msg = MIMEMultipart()
        self.smtp_conn = smtplib.SMTP(EnvoiGMail.SMTP_SERVER, EnvoiGMail.SMTP_PORT)
        self.login_init()

    def password_init(self, passw):
        password = keyring.get_password(EnvoiGMail.SMTP_SERVER, self.username)
        if password is None:
            password = passw
            keyring.set_password(EnvoiGMail.SMTP_SERVER, self.username, password)
        return password

    def login_init(self):  # Création de la connexion SMTP
        self.smtp_conn.ehlo()
        self.smtp_conn.starttls()  # Initialisation de la connexion sécurisée TLS
        self.smtp_conn.ehlo()
        self.smtp_conn.login(self.username, self.password)

    def mail_set_body(self, dest_email, objet, message):  # Envoi d'un message
        self.msg['From'] = self.username
        self.msg['To'] = dest_email
        self.msg['Subject'] = objet
        text = MIMEText(message)
        self.msg.attach(text)

    def mail_set_attach(self, att_file):
        nom_fichier = att_file  # Spécification du nom de la pièce jointe
        with open(nom_fichier, "rb") as attachement:  # Ouverture du fichier
            part = MIMEBase('application', 'octet-stream')  # Encodage de la pièce jointe en Base64
            part.set_payload(attachement.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "piece; filename= %s" % nom_fichier)
            self.msg.attach(part)  # Attache de la pièce jointe à l'objet "message"

    def send_mail(self):
        self.smtp_conn.sendmail(self.msg["From"], self.msg["To"], self.msg.as_string())
        self.smtp_conn.quit()


def main():
    while True:
        mail_adress = input("Adresse mail : ")
        try:
            email = EnvoiGMail(mail_adress)
            logging.info("Connexion établie")
            print("Connexion établie")
            email.mail_set_body(input("Destinataire : "), input("Objet :"), input("Message : "))
            file_path = input("Chemin du fichier : ")
            if file_path != "":
                email.mail_set_attach(file_path)
            email.send_mail()
            logging.info("Email envoyé")
            print("Email envoyé")
            break
        except smtplib.SMTPAuthenticationError:
            logging.warning("Mot de passe ou identifiant incorect")
            print("Mot de passe ou identifiant incorect")


if __name__ == "__main__":
    main()
