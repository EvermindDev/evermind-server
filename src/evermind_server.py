from src.config.config import Config
from flask import Flask, send_from_directory
from flask_cors import CORS

from src.scheduler.jobs_test import JobsTest
from src.services.prompt import Prompt
from src.scheduler.jobs import Jobs
import schedule
import time
import threading
from src.helpers.helper import get_image


class EvermindServer:
    def __init__(self, config):
        self.config = config
        self.app = Flask(__name__)
        CORS(self.app)

        # Initialize routes
        self.initialize_routes()

    def run(self):
        self.start_scheduler()  # Start the scheduler
        self.app.run(port=self.config.APP_PORT, debug=False)  # Start the Flask application

    def initialize_routes(self):
        prompt = Prompt(self.config)
        self.app.route('/v1/stable-diffusion-2-1/run', methods=['POST'])(prompt.create_prompt)
        self.app.route('/v1/stable-diffusion-2-1/status/<string:prompt_uuid>', methods=['GET'])(prompt.get_prompt)
        self.app.route('/static/images/<string:file_name>', methods=['GET'])(get_image)

    def start_scheduler(self):

        if self.config.JOBS_TEST_MODE:
            jobs = JobsTest(self.config)
        else:
            jobs = Jobs(self.config)

        # Schedule the job to run every X seconds
        schedule.every(self.config.JOBS_TIME).seconds.do(jobs.run)

        # Create a separate thread for running the scheduler
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()

    def run_scheduler(self):
        # Run the scheduler continuously within the application context
        with self.app.app_context():
            while True:
                schedule.run_pending()
                time.sleep(1)


def run():
    config = Config()
    EvermindServer(config).run()


if __name__ == '__main__':
    run()
