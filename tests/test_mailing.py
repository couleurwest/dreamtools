import pytest

from src.dreamtools import file_manager
from src.dreamtools import date_manager
from src.dreamtools.mailing_manager import MailController

from tests import Constantine

reference = 'CWI-REQ-20250716-001'
date_test = date_manager.get_today_str(fm='%d-%m-%Y')

#modifier les parametre
dest_name='Jane DOE'
dest_mail='jane.doe@emailk.com'
smtp_url = 'smtp.domaine.net'
smtp_host = 465
smtp_mail = 'ne-pas-repondre@comaine.net'
smtp_password = 'mot-de-passe'
bot_name="Bot Intelligent"

# 🔧 Fixture de configuration mail (dépend de fixation)
@pytest.fixture(scope="session")
def mail_fix(fixation):
    path_template = file_manager.path_build(Constantine.APP_DIR, 'config/mailing.yml')  #emplacement du fichier templates
    Constantine.mailer =  MailController (smtp_url, smtp_host, smtp_mail, smtp_password, path_template, SMTP_USER_NAME=bot_name)

def test_sending_preconfig(mail_fix):
    result = Constantine.mailer.presend(dest_mail,'mail_test', date_test=date_test, dest_name=dest_name, reference=reference)
    assert result == True

def test_sending_custom(mail_fix):
    mail = {
        'subject': 'Test subject',
        'text': """ Bonjour Bonjour {dest_name},
        Nous sommes le {date_test}
        
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent vitae tincidunt dui, porttitor eleifend dui. Duis a porta neque. Suspendisse ut tincidunt justo. Vivamus ut ipsum eu nunc feugiat sodales. Nulla id ligula semper, tincidunt dolor quis, ullamcorper sapien. Aliquam massa felis, placerat id elit sit amet, viverra malesuada velit. Nullam fringilla, urna a mattis semper, justo massa dapibus tellus, at ornare sapien eros et nulla. Etiam venenatis orci pretium, elementum mi nec, bibendum erat. In eget sagittis sapien. Etiam et libero odio. Donec facilisis dapibus arcu, vel aliquet lectus eleifend ac.
Vestibulum congue, tortor sed consequat ultricies, ex felis elementum nibh, sit amet sodales sapien massa nec nunc. Phasellus dapibus malesuada justo et tincidunt. Nulla facilisi. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque consectetur eleifend diam sed ullamcorper. Donec scelerisque scelerisque libero sit amet laoreet. Suspendisse accumsan ut urna at dapibus. Aliquam finibus tellus quis finibus semper. Pellentesque sit amet efficitur massa. Suspendisse eu lectus nibh. Nunc eget pretium tellus, id maximus velit.

Mauris finibus sagittis dui, ut sodales justo dapibus sed. Donec tincidunt posuere mollis. Phasellus rhoncus venenatis massa, eget vehicula neque dignissim eu. Sed pretium vel est quis convallis. Duis a est odio. Mauris et sem eu neque euismod malesuada a in libero. Praesent luctus fringilla nisi, sit amet ultricies elit varius vitae. Nunc eget tortor at velit maximus volutpat non in nisl. In aliquet, dui vel lacinia auctor, leo est interdum metus, quis mollis diam odio a leo. Sed at semper turpis. Quisque congue ligula nec eros hendrerit luctus. Pellentesque a massa nibh. Nullam elit elit, condimentum vel sapien quis, pharetra porttitor elit. Mauris sollicitudin suscipit rutrum. Etiam tempor ex id laoreet rutrum. """,
        'html': """ <b>Bonjour Bonjour {dest_name},</b> 
        Nous sommes le {date_test}

        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent vitae tincidunt dui, porttitor eleifend dui. Duis a porta neque. Suspendisse ut tincidunt justo. Vivamus ut ipsum eu nunc feugiat sodales. Nulla id ligula semper, tincidunt dolor quis, ullamcorper sapien. Aliquam massa felis, placerat id elit sit amet, viverra malesuada velit. Nullam fringilla, urna a mattis semper, justo massa dapibus tellus, at ornare sapien eros et nulla. Etiam venenatis orci pretium, elementum mi nec, bibendum erat. In eget sagittis sapien. Etiam et libero odio. Donec facilisis dapibus arcu, vel aliquet lectus eleifend ac.

Vestibulum congue, tortor sed consequat ultricies, ex felis elementum nibh, sit amet sodales sapien massa nec nunc. Phasellus dapibus malesuada justo et tincidunt. Nulla facilisi. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque consectetur eleifend diam sed ullamcorper. Donec scelerisque scelerisque libero sit amet laoreet. Suspendisse accumsan ut urna at dapibus. Aliquam finibus tellus quis finibus semper. Pellentesque sit amet efficitur massa. Suspendisse eu lectus nibh. Nunc eget pretium tellus, id maximus velit.

Mauris finibus sagittis dui, ut sodales justo dapibus sed. Donec tincidunt posuere mollis. Phasellus rhoncus venenatis massa, eget vehicula neque dignissim eu. Sed pretium vel est quis convallis. Duis a est odio. Mauris et sem eu neque euismod malesuada a in libero. Praesent luctus fringilla nisi, sit amet ultricies elit varius vitae. Nunc eget tortor at velit maximus volutpat non in nisl. In aliquet, dui vel lacinia auctor, leo est interdum metus, quis mollis diam odio a leo. Sed at semper turpis. Quisque congue ligula nec eros hendrerit luctus. Pellentesque a massa nibh. Nullam elit elit, condimentum vel sapien quis, pharetra porttitor elit. Mauris sollicitudin suscipit rutrum. Etiam tempor ex id laoreet rutrum.</p>"""}

    result = Constantine.mailer.presend(dest_mail, 'custom', date_test=date_test, dest_name=dest_name, template_email=mail)
    assert result == True
