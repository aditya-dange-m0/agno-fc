from .auth import router as auth_router
from .projects import router as projects_router
from .tasks import router as tasks_router
from .attachments import router as attachments_router

# Export attachment router via app include if needed