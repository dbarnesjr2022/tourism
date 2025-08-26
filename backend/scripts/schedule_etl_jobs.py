
# pyright: reportMissingTypeStubs=false
from __future__ import annotations

from typing import Any, Callable, Mapping, Protocol, Sequence, Optional, runtime_checkable, List, TypedDict
import subprocess
import time

try:
    # APScheduler has thin/no stubs; tell Pylance to chill on these imports.
    from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore[reportMissingTypeStubs]
    from apscheduler.triggers.cron import CronTrigger  # type: ignore[reportMissingTypeStubs]
except Exception:
    BackgroundScheduler = object  # type: ignore[assignment]
    CronTrigger = object  # type: ignore[assignment]

@runtime_checkable
class SchedulerLike(Protocol):
    def add_job(
        self,
        func: Callable[..., Any],
        trigger: Any | None = ...,
        args: Sequence[Any] | None = ...,
        kwargs: Mapping[str, Any] | None = ...,
        *,
        id: str | None = ...,
        name: str | None = ...,
        misfire_grace_time: Optional[int] | None = ...,
        coalesce: Optional[bool] | None = ...,
        max_instances: Optional[int] | None = ...,
        next_run_time: Any | None = ...,
        jobstore: str = "default",
        executor: str = "default",
        replace_existing: bool = False,
        **trigger_args: Any,
    ) -> Any: ...
    def start(self) -> None: ...
    def shutdown(self, wait: bool = True) -> None: ...

class TriggerConfig(TypedDict):
    type: str
    hour: str
    minute: str

class JobConfig(TypedDict):
    name: str
    script: str
    trigger: TriggerConfig

# Define jobs: each job runs a script
JOBS: List[JobConfig] = [
    {
        "name": "Fetch Event Calendars",
        "script": "backend/scripts/fetch_event_calendars.py",
        "trigger": {"type": "cron", "hour": "2", "minute": "0"},  # daily at 2:00 AM
    },
    {
        "name": "Fetch Weather Data",
        "script": "backend/scripts/fetch_weather_data.py",
        "trigger": {"type": "cron", "hour": "2", "minute": "30"},  # daily at 2:30 AM
    },
    {
        "name": "Fetch Competitor Prices",
        "script": "backend/scripts/fetch_competitor_prices.py",
        "trigger": {"type": "cron", "hour": "3", "minute": "0"},  # daily at 3:00 AM
    },
    {
        "name": "Ingest Historical Bookings",
        "script": "backend/scripts/ingest_historical_bookings.py",
        "trigger": {"type": "cron", "hour": "3", "minute": "30"},  # daily at 3:30 AM
    },
    {
        "name": "Store Data in Postgres",
        "script": "backend/scripts/store_data_postgres.py",
        "trigger": {"type": "cron", "hour": "4", "minute": "0"},  # daily at 4:00 AM
    },
]


def run_script(script_path: str) -> None:
    print(f"Running ETL job: {script_path}")
    subprocess.run(["python", script_path], check=False)


def schedule_jobs() -> None:
    scheduler: SchedulerLike = BackgroundScheduler(timezone="UTC")  # type: ignore[call-arg]
    for job in JOBS:
        trigger: TriggerConfig = job["trigger"]
        scheduler.add_job(
            run_script,
            trigger["type"],
            args=[job["script"]],
            hour=trigger["hour"],
            minute=trigger["minute"],
            id=job["name"],
            name=job["name"],
            replace_existing=True,
        )
    scheduler.start()
    print("ETL job scheduler started. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")


if __name__ == "__main__":
    schedule_jobs()

# Note: APScheduler does not ship type stubs. You can ignore Pylance 'reportMissingTypeStubs' for this library.
