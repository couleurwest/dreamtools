import re
import uuid
from datetime import date

from cerberus import Validator, TypeDefinition
from cerberus.validator import schema_registry

from . import toolbox

# --- Types personnalisés ---
custom_types = {
    'uuid': TypeDefinition('uuid', (uuid.UUID, ), ()),
    'date': TypeDefinition('date', (date,), ()),
    'phone': TypeDefinition('phone', (str,), ()),
    'password': TypeDefinition('password', (str,), ()), }


# --- Fonction de nettoyage ---
def normalize_phone(value):
    if not isinstance(value, str):
        return value or ''
    value = value.strip()
    if value.startswith('+'):
        value = '+' + re.sub(r'[^\d]', '', value[1:])
    else:
        value = re.sub(r'[^\d]', '', value)

    match = re.match(r'(00|\+)?(\d+)(\d{3})(\d{3})(\d{3})', value)
    if match:
        prefix = ''
        groups = match.groups()
        if groups[0] == '+':
            prefix = '+'
            groups = groups[1:]
        elif groups[0] is None:
            groups = groups[1:]
        return prefix + ' '.join(groups)
    return value or ''


class DreamRegistry:
    email = {'type': 'string', 'is_email': True, 'coerce': lambda v: '' if v is None else v, 'empty': True}
    password = {'type': 'string', 'is_password': True, 'empty': False}
    url = {'type': 'string', 'is_url': True, 'coerce': lambda v: '' if v is None else v, 'empty': True}
    varchar = {'type': 'string', 'coerce': toolbox.clean_space, 'maxlength': 255, 'empty': True, }
    referenco = {'type': 'string', 'coerce': toolbox.clean_allspace, 'maxlength': 15, 'empty': True, }
    referenco_short = {'type': 'string', 'coerce': toolbox.clean_allspace, 'maxlength': 4, 'empty': True, }
    phone = {'type': 'string', 'coerce': normalize_phone, 'is_phone': True, 'empty': True, }
    is_digit = {'type': 'integer', 'coerce': lambda v: int(v) if v and (isinstance(v, int) or v.isdigit()) else v}


# --- Schémas génériques enregistrés ---
schema_registry.add('email_schema', {'email': {'type': 'string', 'regex': toolbox.RGX_EMAIL}})
schema_registry.add('email_schema', {'email': DreamRegistry.email})
schema_registry.add('password_schema', {'password': DreamRegistry.password})
schema_registry.add('phone_number_schema', {'phone': DreamRegistry.phone})
schema_registry.add('url_schema', {'url': DreamRegistry.url})
schema_registry.add('link_schema', {'link': DreamRegistry.url})

schema_registry.add('contact_info_schema',
                    {'email': DreamRegistry.email, 'phone_1': DreamRegistry.phone, 'phone_2': DreamRegistry.phone,
                        'oneof': [{'email': {'required': True}}, {'phone_1': {'required': True}},
                                  {'phone_2': {'required': True}}]})

schema_registry.add('authentication_schema', {'email': DreamRegistry.email | {'required': True},
    'password': DreamRegistry.password | {'required': True}})

schema_registry.add('signin_schema', {'email': DreamRegistry.email | {'required': True},
    'password': DreamRegistry.password | {'required': True},
    'confirmpassword': DreamRegistry.password | {'required': True}})


# --- Validator personnalisé ---
class DreamValidator(Validator):
    types_mapping = Validator.types_mapping.copy()
    types_mapping.update(custom_types)

    def _validate_is_email(self, is_email, field, value):
        """ {'type': 'boolean'} """
        if is_email and not toolbox.is_valid_email(value):
            self._error(field, "L'adresse email est invalide.")

    def _validate_is_url(self, is_url, field, value):
        """ {'type': 'boolean'} """
        if is_url and not toolbox.is_valid_url(value):
            self._error(field, "L'URL est invalide.")

    def _validate_is_password(self, is_password, field, value):
        """ {'type': 'boolean'} """
        if is_password and not toolbox.is_valid_password(value):
            self._error(field, "Le mot de passe est invalide.")

    def _validate_is_phone(self, is_phone, field, value):
        """ {'type': 'boolean'} """
        if is_phone and not toolbox.is_valid_phone(value):
            self._error(field, "Le numéro de téléphone est invalide.")


# --- Fonction générique de validation ---
def validate_data(data: dict, schema_name: str = None, schema: dict = None) -> tuple[bool, dict]:
    """
    Valide les données selon un schéma donné ou un nom de schéma enregistré.

    :param data: Données à valider.
    :param schema_name: Nom d’un schéma enregistré dans schema_registry.
    :param schema: Schéma inline personnalisé.
    :return: Tuple (est_valide, erreurs).

    :Exemple:
    data = { 'email': 'test@exemple.com', 'phone_number': normalize_phone('06 90 12 34 56')}
    ok, errors = validate_data(data, schema_name='contact_info_schema')

    if ok:
        print("✓ Données valides")
    else:
        print("✗ Erreurs :", errors)
    """
    if schema_name:
        schema = schema_registry.get(schema_name)
        if not schema:
            raise ValueError(f"Schéma '{schema_name}' non trouvé dans le registre.")

    if not schema:
        raise ValueError("Aucun schéma fourni pour la validation.")

    validator = DreamValidator(schema)
    is_valid = validator.validate(data)
    return is_valid, validator.errors
