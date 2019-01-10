import asyncio

from mattermost.notify import notify
import monitors.load_monitors
from monitors.monitor import Monitor
from scheduler import scheduler
from server import run_server


async def main():
    await notify("Tromino: Starting...")

    scheduler.start()
    await notify("Tromino: Scheduler up")

    monitor_types = monitors.load_monitors()
    await notify(f"Tromino: Loading plugins - {', '.join([m for m in monitor_types])}")

    # job = scheduler.add_job(lambda: print(1), "interval", seconds=5)
    monitor_instances = await Monitor.load_all()
    await notify(
        f"Tromino: Loading monitor instances - {len(monitor_instances)} instances"
    )

    await run_server()
    await notify("Tromino: HTTP Server stared")

    await notify("Tromino: Hello ! What could I do for you ?")


asyncio.ensure_future(main())
asyncio.get_event_loop().run_forever()
