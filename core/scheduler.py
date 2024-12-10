from apscheduler.schedulers.background import BackgroundScheduler
import logging
from datetime import datetime


class Scheduler:
    def __init__(self):
        """
        Initialize the task scheduler.
        """
        self.scheduler = BackgroundScheduler()
        self.logger = logging.getLogger("Scheduler")
        logging.basicConfig(level=logging.INFO)

    def add_task(self, task_id, func, trigger, **kwargs):
        """
        Add a new task to the scheduler.
        :param task_id: Unique identifier for the task.
        :param func: Function to execute.
        :param trigger: Trigger type (e.g., "interval", "cron").
        :param kwargs: Additional arguments for the trigger.
        """
        try:
            self.scheduler.add_job(func, trigger, id=task_id, **kwargs)
            self.logger.info(f"Task {task_id} added with trigger: {trigger}")
        except Exception as e:
            self.logger.error(f"Error adding task {task_id}: {e}")

    def remove_task(self, task_id):
        """
        Remove a task from the scheduler.
        :param task_id: Unique identifier for the task.
        """
        try:
            self.scheduler.remove_job(task_id)
            self.logger.info(f"Task {task_id} removed.")
        except Exception as e:
            self.logger.error(f"Error removing task {task_id}: {e}")

    def list_tasks(self):
        """
        List all scheduled tasks.
        :return: List of job details.
        """
        jobs = self.scheduler.get_jobs()
        task_list = [{"id": job.id, "next_run": job.next_run_time, "trigger": str(job.trigger)} for job in jobs]
        self.logger.info(f"Scheduled tasks: {task_list}")
        return task_list

    def start(self):
        """
        Start the scheduler.
        """
        self.scheduler.start()
        self.logger.info("Scheduler started.")

    def shutdown(self):
        """
        Shutdown the scheduler.
        """
        self.scheduler.shutdown(wait=False)
        self.logger.info("Scheduler shut down.")


if __name__ == "__main__":
    # Example usage
    def sample_task():
        print(f"Task executed at {datetime.now()}")

    scheduler = Scheduler()

    # Add a task to run every 5 seconds
    scheduler.add_task("sample_task", func=sample_task, trigger="interval", seconds=5)

    # Start the scheduler
    scheduler.start()

    # Allow it to run for 15 seconds
    import time
    time.sleep(15)

    # Shutdown the scheduler
    scheduler.shutdown()
