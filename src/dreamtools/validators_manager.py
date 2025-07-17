from cerberus.validator import Validator, schema_registry
from . import toolbox

# Enregistrements de schémas génériques pour réutilisation
schema_registry.add('email_schema', {'email': {'type': 'string', 'regex': toolbox.RGX_EMAIL}})
schema_registry.add('password_schema', {'password': {'type': 'string', 'regex': toolbox.RGX_PWD}})
schema_registry.add('phone_number_schema', {'phone_number': {'type': 'string', 'regex': toolbox.RGX_PHONE}})
schema_registry.add('link_web_schema', {'link_web': {'type': 'string', 'regex': toolbox.RGX_URL}})

# Validateur pour les emails
class EmailValidator(Validator):
    def _validate_is_email(self, is_email, field, value):
        """
        Vérifie si une adresse email est syntaxiquement valide.

        L'option `is_email` doit être un booléen dans le schéma :

        Exemple :
            {'email': {'type': 'string', 'is_email': True}}
        """
        if is_email and not toolbox.is_valid_email(value):
            self._error(field, "L'adresse email est invalide.")

# Validateur pour les URLs
class UrlValidator(Validator):
    def _validate_is_url(self, is_url, field, value):
        """
        Vérifie si une URL est syntaxiquement valide.

        L'option `is_url` doit être un booléen dans le schéma :

        Exemple :
            {'link': {'type': 'string', 'is_url': True}}
        """
        if is_url and not toolbox.is_valid_url(value):
            self._error(field, "L'URL est invalide.")

# Validateur pour les mots de passe
class PasswordValidator(Validator):
    def _validate_is_password(self, is_password, field, value):
        """
        Vérifie si un mot de passe respecte les règles de complexité.

        L'option `is_password` doit être un booléen dans le schéma :

        Exemple :
            {'password': {'type': 'string', 'is_password': True}}
        """
        if is_password and not toolbox.is_valid_password(value):
            self._error(field, "Le mot de passe est invalide.")
