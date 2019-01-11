import asyncio

from exceptions import JobAlreadyStarted
from mattermost.notify import notify
from monitors.monitor import Monitor
from scheduler import scheduler
from server import run_server
import monitors


async def main():
    await notify("Tromino: Starting...")

    scheduler.start()
    await notify("Tromino: Scheduler up")

    monitor_types = monitors.load_monitors()
    await notify(f"Tromino: Loading plugins - {', '.join([m for m in monitor_types])}")

    # job = scheduler.add_job(lambda: print(1), "interval", seconds=5)
    monitor_instances = await Monitor.load_all()
    await notify(f"Tromino: Loading monitor instances - {len(monitor_instances)}")

    for m in monitor_instances:
        try:
            await monitor_instances[m].job_start()
            await notify(f"Tromino: Starting {m}")
        except JobAlreadyStarted:
            pass

    await run_server()
    await notify("Tromino: HTTP Server stared")

    await notify("Tromino: Hello ! What could I do for you ?")


asyncio.ensure_future(main())
asyncio.get_event_loop().run_forever()
