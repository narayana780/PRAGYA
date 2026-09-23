from fastapi import APIRouter

from app.api.v1.endpoints import health
from app.modules.assessments.router import router as assessments_router
from app.modules.competencies.router import (
    competencies_router,
    domains_router,
    proficiency_router,
    role_competencies_router,
)
from app.modules.departments.router import router as departments_router
from app.modules.employees.router import router as employees_router
from app.modules.job_roles.router import router as job_roles_router
from app.modules.skill_gaps.router import router as skill_gaps_router
from app.modules.training_history.router import router as training_history_router

api_router = APIRouter()

# Register core health endpoints
api_router.include_router(health.router, tags=["Health"])

# Register organizational domain routers
api_router.include_router(departments_router)
api_router.include_router(job_roles_router)
api_router.include_router(employees_router)
api_router.include_router(training_history_router)

# Register competency framework domain routers
api_router.include_router(competencies_router)
api_router.include_router(domains_router)
api_router.include_router(proficiency_router)
api_router.include_router(role_competencies_router)

# Register assessments & evidence domain router
api_router.include_router(assessments_router)

# Register skill gaps domain router
api_router.include_router(skill_gaps_router)

# Register personalized learning recommendations router
from app.modules.recommendations.router import router as recommendations_router

api_router.include_router(recommendations_router)

# Register document intelligence & materials router
from app.modules.materials.router import router as materials_router

api_router.include_router(materials_router)

# Register RAG semantic evidence retrieval router
from app.modules.rag.router import router as rag_router

api_router.include_router(rag_router)

# Register PRAGYA AI Learning Assistant router
from app.modules.assistant.router import router as assistant_router

api_router.include_router(assistant_router)

# Register Stage 10 AI Quiz & MCQ Generation router
from app.modules.quizzes.router import router as quizzes_router

api_router.include_router(quizzes_router)

# Register Stage 11 Adaptive Assessment & Closed-Loop Recalibration router
from app.modules.adaptive.router import router as adaptive_router

api_router.include_router(adaptive_router)

# Register Stage 12 Statistical Virtual Lab routers
from app.modules.labs.router import labs_router, lab_sessions_router

api_router.include_router(labs_router)
api_router.include_router(lab_sessions_router)

# Register Complete Course Learning Path router
from app.modules.courses.router import router as courses_router

api_router.include_router(courses_router)

# Register Stage 13 Employee Performance Analysis & Longitudinal Tracking router
from app.modules.analytics.router import router as analytics_router

api_router.include_router(analytics_router)

# Register Stage 14 Administrator Workforce Intelligence & Cadre Analytics router
from app.modules.analytics.admin_router import router as admin_router

api_router.include_router(admin_router)

# Register Stage 18 Official Reporting & Audit Compliance Export router
from app.modules.reports.router import router as reports_router

api_router.include_router(reports_router)

