class Reponce:
    status:int
    detail = None
    message:str
    title:str

    def __init__(self, message:str='Opération réussie', title:str='', status:int=200, *args, **kwargs):
        self.status = status
        self.detail = args or kwargs
        self.message = message
        self.title = title


    @property
    def succeed(self):
        """ Renvoie le status de la réponse

        :rtype: bool
        """
        return 200 <= self.status < 300



class ExceptionManager(Exception):
    """
    Exception personnalisée avec suivi automatique via le tracker.

    :param message: Message lisible destiné à l’utilisateur.
    :param status: Code HTTP de l’erreur.
    :param title: Titre bref, destiné aux logs et à l’interface.
    """

    def __init__(self, message="Une erreur interne est survenue.", title='ERROR SYSTEM', status=500, **kwargs):
        super().__init__(message, title, status)

        self.message = message
        self.title = title
        self.status = status
        self.detail = kwargs


    def __str__(self):
        return str(f'[{self.title}] : self.message - {self.status}')

class RequestException(ExceptionManager):
    def __init__(self):
        super().__init__(
            "Le format ou le contenu de la requête n’est pas accepté.",
            "Requête non acceptable",
            406
        )


class AuthException(ExceptionManager):
    def __init__(self):
        super().__init__(
            "Identifiants incorrects. Veuillez vérifier votre login ou mot de passe.",
            "Échec d’authentification",
            401
        )


class OAuthException(ExceptionManager):
    def __init__(self):
        super().__init__(
            "Vous n’avez pas les autorisations nécessaires pour accéder à cette ressource.",
            "Accès interdit",
            403
        )


class OAuthElapsedException(ExceptionManager):
    def __init__(self):
        super().__init__(
            "Le délai d’authentification a expiré. Veuillez recommencer.",
            "Délai dépassé",
            408
        )


class UExistException(ExceptionManager):
    def __init__(self):
        super().__init__(
            "Ce compte existe déjà. Veuillez utiliser une autre adresse ou réinitialiser votre mot de passe.",
            "Conflit d'identité",
            409
        )


class AccountException(ExceptionManager):
    def __init__(self):
        super().__init__(
            "Aucun compte correspondant n’a été trouvé.",
            "Compte introuvable",
            404
        )


class RessourceException(ExceptionManager):
    def __init__(self):
        super().__init__(
            "La ressource demandée est introuvable ou n’existe plus.",
            "Ressource introuvable",
            404
        )


class PageException(ExceptionManager):
    def __init__(self):
        super().__init__(
            "La page que vous cherchez n’existe pas.",
            "Page non trouvée",
            404
        )


class ParamsException(ExceptionManager):
    def __init__(self):
        super().__init__(
            "Les données soumises sont invalides ou incomplètes.",
            "Paramètres incorrects",
            400
        )


class TooManyRequests(ExceptionManager):
    def __init__(self):
        super().__init__(
            "Trop de requêtes ont été envoyées en peu de temps. Merci de patienter avant de réessayer.",
            "Requêtes trop fréquentes",
            429
        )