from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.core.config import settings
from app.db.base import Base
from app.modules.assessments.models import (  # noqa: F401
    Assessment,
    AssessmentAttempt,
    AssessmentCompetency,
    AssessmentQuestion,
    AssessmentResponse,
    CompetencyEvidence,
    CompetencyScoreHistory,
    EmployeeCompetency,
)
from app.modules.competencies.models import (  # noqa: F401
    Competency,
    CompetencyDomain,
    CompetencyRelationship,
    CompetencyRequirement,
    Course,
    CourseCompetency,
    ProficiencyLevel,
    TrainingProgramme,
    TrainingProgrammeCompetency,
)
from app.modules.departments.models import Department  # noqa: F401
from app.modules.employees.models import Employee  # noqa: F401
from app.modules.job_roles.models import JobRole  # noqa: F401
from app.modules.skill_gaps.models import SkillGap  # noqa: F401
from app.modules.training_history.models import TrainingHistory  # noqa: F401
from app.modules.courses.models import (  # noqa: F401
    LearningItem,
    LearningItemCompetency,
    CourseProgress,
    CourseResourceProgress,
    ModuleActivityAttempt,
)
from app.modules.recommendations.models import (  # noqa: F401
    LearningRecommendation,
    LearningPath,
    LearningPathItem,
)
from app.modules.materials.models import (  # noqa: F401
    UploadedMaterial,
    Document,
    DocumentChunk,
)
from app.modules.labs.models import (  # noqa: F401
    LabDataset,
    LabScenario,
    LabSession,
    LabAction,
    LabResult,
)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# Ensure sqlalchemy.url uses a sync driver for standard alembic operations
sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "")
config.set_main_option("sqlalchemy.url", sync_db_url)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
