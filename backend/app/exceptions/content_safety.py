class ContentSafetyError(Exception):
    """Erro relacionado à análise de conteúdo."""


class ContentSafetyServiceError(ContentSafetyError):
    """Erro ao comunicar com o Azure Content Safety."""