class WebBookError(Exception):
    """Exception de base pour les erreurs métier de WebBook."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class EmailDejaUtiliseError(WebBookError):
    """Levée lorsqu'un email est déjà associé à un compte existant."""


class IdentifiantsInvalidesError(WebBookError):
    """Levée lorsque l'email ou le mot de passe est incorrect."""


class RessourceIntrouvableError(WebBookError):
    """Levée lorsqu'une ressource demandée n'existe pas ou n'appartient pas à l'utilisateur."""


class ConflitMetierError(WebBookError):
    """Levée en cas de conflit de règle métier (doublon, catégorie non vide, etc.)."""


class ValidationMetierError(WebBookError):
    """Levée lorsqu'une règle de validation métier n'est pas respectée."""


class EnvoiEmailError(WebBookError):
    """Levée lorsque l'envoi d'un email transactionnel échoue."""
