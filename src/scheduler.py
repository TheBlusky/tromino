from pytz import utc
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor


def create_scheduler():
    new_scheduler = AsyncIOScheduler(
        jobstores={"default": MemoryJobStore()},
        executors={"default": AsyncIOExecutor()},
        job_defaults={"coalesce": False, "max_instances": 3},
        timezone=utc,
    )
    return new_scheduler


scheduler = create_scheduler()
