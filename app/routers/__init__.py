from app.models.service import LocalLLMService

_service = None

def get_service() -> LocalLLMService:
    global _service
    if _service is None:
        _service = LocalLLMService()
    return _service
