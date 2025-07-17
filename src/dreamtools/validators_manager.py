from cerberus.validator import Validator, schema_registry

from . import toolbox

schema_registry.add('email scheme', {'email': {'type': 'string', 'regex': toolbox.RGX_EMAIL}})
schema_registry.add('password scheme', {'password': {'type': 'string', 'regex': toolbox.RGX_PWD}})
schema_registry.add('phone_number scheme', {'phone_number': {'type': 'string', 'regex': toolbox.RGX_PHONE}})
schema_registry.add('link_web scheme', {'link_web': {'type': 'string', 'regex': toolbox.RGX_URL}})


class EmailValidator(Validator):
    def _validate_is_email(self, is_email, field, value):
        """
        Vérifie qu'une adresse email est syntaxiquement et fonctionnellement correcte.

        L'option `is_email` est un booléen dans le schéma.

        Exemple de schéma :
            {'email': {'type': 'string', 'is_email': True}}
        """
        if is_email and not toolbox.is_valid_email(value):
            self._error(field, "L'adresse email est invalide.")

class UrlValidator(Validator):
    def _validate_is_url(self, is_url, field, value):
        """
        Vérifie qu'une adresse email est syntaxiquement et fonctionnellement correcte.

        L'option `is_email` est un booléen dans le schéma.

        Exemple de schéma :
            {'email': {'type': 'string', 'is_email': True}}
        """
        if is_url and not toolbox.is_valid_url(value):
            self._error(field, "L'adresse email est invalide.")

class PasswordValidator(Validator):
    def _validate_is_password(self, password, field, value):
        """
        Vérifie qu'une adresse email est syntaxiquement et fonctionnellement correcte.

        L'option `is_email` est un booléen dans le schéma.

        Exemple de schéma :
            {'email': {'type': 'string', 'is_email': True}}
        """
        if password and not toolbox.is_valid_password(value):
            self._error(field, "L'adresse email est invalide.")