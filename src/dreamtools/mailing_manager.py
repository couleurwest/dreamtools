# -*- coding: utf-8 -*-
# mail_objecting_manager.py

__all__ = ['MailController']

import os
from email import encoders
from email.mime.base import MIMEBase

"""
Module de Gestion de mail_object préparés

pathfile : dreamtools-dreamgeeker/mail_objecting_manager.py

Pré-Requis
-------------
.. warning::

    Indiquer les parametres smtp dans le fichiers de configuration <PROJECT_NAME>/cfg/.app.yml

.. code-block:: YAML

    SMTP_HOST: smtp-host_adresse
    SMTP_PORT: port_smtp
    SMTP_AUTHmail_object: mail_object_authen
    SMTP_AUTHPWD: password_auth
    SMTP_USERNAME : name_sender <template_email>

.. warning::

    Les mail_objects sont à définir dans le ficchier <PROJECT_NAME>/cfg/mail_objecting.yml au format suivant

.. code-block:: YAML

     footer:
      html: <Pied de mail_object unique pour tous les mail_objects (signature, rgpd...)>
      text: <Pied de mail_object unique pour tous les mail_objects (signature, rgpd...)>
     code_mail_object:
      html: <ici mail_object au format HTML>
      text : <Le mail_object au format texte>
      objt : <Objet du mail_object>


"""
import dataclasses
import smtplib
import ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config_manager import ConfigController
from .tracking_manager import TrackingManager


@dataclasses.dataclass
class MailController:
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_AUTH_EMAIL: str
    SMTP_AUTH_PWD: str
    PATH_TEMPLATES: str # = '.cfg/mail_objecting.yml'
    SMTP_USER_NAME:str = 'ne-pas-repondre'
    SMTP_IDENTITY: str =''

    def __post_init__(self):
        self.SMTP_IDENTITY = f"{self.SMTP_USER_NAME} <{self.SMTP_AUTH_EMAIL}>"

    def send_mail(self, subject:str, receivers:str, d_msg, to_receiver:str =None, **kwargs):
        """ Envoie du mail_object

        :param subject: Sujet du mail_object
        :param receivers: template_email destinataire
        :param d_msg: Message
        :param to_receiver: Nom destinataire
        :return:
        """

        TrackingManager.flag("SEND_mail_object : Paramétrage smtp")
        context = ssl.create_default_context()

        TrackingManager.flag("SEND_mail_object:Paramétrage message MIME")
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.SMTP_IDENTITY
        message["To"] = to_receiver or receivers

        if 'cc' in kwargs:
            message["Cc"] = kwargs.pop('cc')

        if 'cci' in kwargs:
            message["Cci"] = kwargs.pop('cci')

        TrackingManager.flag("SEND_mail_object:Paramétrage contenu mail_object")
        content = d_msg.get('text')
        content = MIMEText(content, 'plain', 'utf-8')
        message.attach(content)

        if d_msg.get('html'):
            content = d_msg.get('html')
            content = MIMEText(content, "html")
            message.attach(content)

        if kwargs.get('file'):
            attachements = kwargs.pop('file')
            filename = os.path.basename(attachements)

            with open(attachements, "rb") as attachment:
                content = MIMEBase('wwwcwest', 'octate-stream', Name=filename)
                content.set_payload(attachment.read())

            encoders.encode_base64(content)
            content.add_header('Content-Disposition', f"attachment'; filename={filename}")
            message.attach(content)

        TrackingManager.flag("SEND_mail_object:Connexion SMTP")
        with smtplib.SMTP_SSL(self.SMTP_HOST, self.SMTP_PORT, context=context) as server:
            TrackingManager.flag("SEND_mail_object:Authentification")
            server.login(self.SMTP_AUTH_EMAIL, self.SMTP_AUTH_PWD)
            TrackingManager.flag("SEND_mail_object: Sending")
            server.sendmail(self.SMTP_AUTH_EMAIL, receivers, message.as_string())

        return True

    def presend(self, email:str, code:str, dest_name:str = '', attachement=None, dest_cc=None, dest_cci=None, **data_field):
        """
            Prépare un e-mail avant envoi en chargeant un modèle de message et en injectant les données.

            Cette fonction charge un template d'e-mail (texte + HTML + sujet) selon un code donné,
            le personnalise avec les données fournies, puis appelle la fonction d'envoi.

            Parameters
            ----------
            email : str
                Adresse e-mail du destinataire.
            code : str
                Clé de référence du modèle à charger. Si 'custom', alors un template personnalisé doit être passé via `template_data`.
            dest_name : str, optional
                Nom du destinataire (ex. "Mme Dupont"), utilisé pour l'affichage ou l'injection dans le template.
            **data_field :
                Données de remplissage du template (ex. nom, date, référence). Si `code == 'custom'`, un champ `template_data` est attendu :
                `template_data = {'text': str, 'html': str, 'subject': str}`.

            Returns
            -------
            bool
                `True` si l'envoi s'est bien déroulé, sinon `False`.

            Example
            -------
            presend (
                email="client@example.com",
                code="confirmation",
                dest_name="Mme Dupont",
                nom="Marie",
                date="16 juillet 2025"
            )
            :param dest_name:
            :param code:
            :param email:
            :param dest_cci:
            :param dest_cc:
            :param attachement: """
        TrackingManager.flag(f'PRESEND:Loading template {code}')
        if code == 'custom' and data_field.get('template_email'):
            template_email = data_field['template_email']
        else:
            template_email = ConfigController.loading(self.PATH_TEMPLATES, code)
            footer = ConfigController.loading(self.PATH_TEMPLATES, 'footer') or {'text':'', 'html':''}
            template_email['text'] += footer['text']
            template_email['html'] += footer['html']

        TrackingManager.flag('PRESEND: Preparation')

        data_field['dest_name']= dest_name

        part1 = template_email['text'].format(**data_field)
        part2 = template_email['html'].format(**data_field)

        to_receiver = fr'{dest_name} <{email}>'

        item_tracking =f'**************************** Envoi ({code}) -> {email}'
        TrackingManager.flag(item_tracking)
        send = TrackingManager.fntracker(self.send_mail, item_tracking, template_email.get('subject'),
                                         email, {'text': part1, 'html': part2}, to_receiver,
                                         attachment=attachement, cc=dest_cc, cci=dest_cci)

        return send.succeed
