from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.courses.models import LearningItem
from app.modules.recommendations.providers.base import LearningProvider, ProviderInfo
from app.modules.recommendations.providers.mock_igot import MockIGOTProvider
from app.modules.recommendations.providers.mock_nssta import MockNSSTAProvider
from app.modules.recommendations.providers.pragya_provider import PragyaLearningProvider


class ProviderRegistry:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._providers: dict[str, LearningProvider] = {
            "IGOT": MockIGOTProvider(db),
            "NSSTA_TPAC": MockNSSTAProvider(db),
            "PRAGYA": PragyaLearningProvider(db),
        }

    def get_provider(self, code: str) -> LearningProvider | None:
        return self._providers.get(code.upper())

    def get_all_providers(self) -> list[LearningProvider]:
        return list(self._providers.values())

    async def list_provider_infos(self) -> list[ProviderInfo]:
        infos: list[ProviderInfo] = []
        for code, provider in self._providers.items():
            stmt = select(func.count(LearningItem.id)).where(
                LearningItem.provider == code,
                LearningItem.is_active.is_(True),
            )
            res = await self.db.execute(stmt)
            count = res.scalar_one() or 0
            infos.append(provider.get_info(catalogue_count=count))
        return infos
