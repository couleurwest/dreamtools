from cerberus.validator import Validator, schema_registry
from . import toolbox
from cerberus import Validator, TypeDefinition
import re
# Enregistrements de schémas génériques pour réutilisation
schema_registry.add('email_schema', {'email': {'type': 'string', 'regex': toolbox.RGX_EMAIL}})
schema_registry.add('password_schema', {'password': {'type': 'string', 'regex': toolbox.RGX_PWD}})
schema_registry.add('phone_number_schema', {'phone_number': {'type': 'string', 'regex': toolbox.RGX_PHONE}})
schema_registry.add('link_web_schema', {'link_web': {'type': 'string', 'regex': toolbox.RGX_URL}})

# Validateur pour les emails

custom_types = {
    'phone': TypeDefinition('phone', (str,), ()),
    'password': TypeDefinition('password', (str,), ()),
}

# --- Validator principal ---
class DreamValidator(Validator):
    types_mapping = Validator.types_mapping.copy()
    types_mapping.update(custom_types)

    def _validate_is_email(self, is_email, field, value)->bool:
        """ {'type': 'boolean'} """
        if is_email and not toolbox.is_valid_email(value):
            self._error(field, "L'adresse email est invalide.")

    def _validate_is_url(self, is_url, field, value)->bool:
        """ {'type': 'boolean'} """
        if is_url and not toolbox.is_valid_url(value):
            self._error(field, "L'URL est invalide.")

    def _validate_is_password(self, is_password, field, value)->bool:
        """ {'type': 'boolean'} """
        if is_password and not toolbox.is_valid_password(value):
            self._error(field, "Le mot de passe est invalide.")

    def _validate_is_phone(self, is_phone, field, value)->bool:
        """ {'type': 'boolean'} """
        if is_phone and not toolbox.is_valid_phone(value):
            self._error(field, "Le numéro de téléphone est invalide.")

def normalize_phone(value):
    if not isinstance(value, str):
        return value or ''

    # Nettoyer : garder uniquement chiffres et +, et seulement un + au début
    value = value.strip()
    if value.startswith('+'):
        value = '+' + re.sub(r'[^\d]', '', value[1:])
    else:
        value = re.sub(r'[^\d]', '', value)

    # Numéro international : +XXX...
    match = re.match(r'(00|\+)?(\d+)(\d{3})(\d{3})(\d{3})', value)
    if match:
        prefix = ''
        groups= match.groups()
        if groups[0] == '+' :
            prefix = '+'
            groups = groups[1:]
        elif groups[0] is None:
            groups = groups[1:]
        grouped = prefix + ' '.join(groups)
        return grouped

    return value or ''


class DreamRegistry:
    email = {
        'type': 'string',
        'regex': r'^[^@\s]+@[^@\s]+\.[a-zA-Z0-9]{2,}$',
        'coerce': lambda v: '' if v is None else v,
        'empty': True}
    url = {
        'type': 'string',
        'regex': r'^((https?://)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}))?$',  # URL valide
        'coerce': lambda v: '' if v is None else v,
        'empty': True
    }
    varchar = {
        'type': 'string',
        'coerce': toolbox.clean_space,
        'maxlength': 250,
        'empty': True,
    }
    referenco = {
        'type': 'string',
        'coerce': toolbox.clean_space,
        'maxlength': 15,
        'empty': True,
    }
    referenco_short = {
        'type': 'string',
        'coerce': toolbox.clean_space,
        'maxlength': 4,
        'empty': True,
    }
    phone = {
        'type': 'string',
        'coerce': normalize_phone,
        'regex': r'^(\+|00)?\d[\d ]+$',  # accepte + ou 00, suivi de chiffres et espaces
        'empty': True,
    }
    is_digit = {
        'type': 'integer',
        'coerce': lambda v: int(v) if v and (isinstance(v, int) or v.isdigit()) else v}

