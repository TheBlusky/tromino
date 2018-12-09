from pytz import utc
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

jobstores = {"default": MemoryJobStore()}
executors = {"default": AsyncIOExecutor()}
job_defaults = {"coalesce": False, "max_instances": 3}
scheduler = AsyncIOScheduler(
    jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc
)
