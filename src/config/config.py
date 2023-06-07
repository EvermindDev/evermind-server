import configparser
import os

CONFIG_FILE_NAME = "config.cfg"
APP_CONFIG_SECTION = "app"
FILE_CONFIG_SECTION = "file-data"
STORAGE_CONFIG_SECTION = "storage"
LOGS_CONFIG_SECTION = "logs"
MODELS_CONFIG_SECTION = "models"
JOBS_CONFIG_SECTION = "jobs"
TEST_CONFIG_SECTION = "test"


class Config:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_NAME)

        self.APP_ENV = config.get(APP_CONFIG_SECTION, "app_env")
        self.APP_DEBUG = eval(config.get(APP_CONFIG_SECTION, "app_debug"))
        self.APP_URL = config.get(APP_CONFIG_SECTION, "app_url")
        self.APP_PORT = config.get(APP_CONFIG_SECTION, "app_port")
        self.APP_API_KEY = config.get(APP_CONFIG_SECTION, "app_api_key")

        data_directory = config.get(FILE_CONFIG_SECTION, "data_directory")

        if data_directory:
            data_directory_path = os.getcwd() + '/' + eval(data_directory)
        else:
            data_directory_path = os.getcwd() + '/data'

        self.DATA_DIRECTORY = data_directory_path

        self.DATA_USE_LOCAL_STORAGE = eval(config.get(STORAGE_CONFIG_SECTION, "use_local_storage"))
        self.IMAGE_STORAGE = eval(config.get(STORAGE_CONFIG_SECTION, "local_image_storage_path"))
        self.IMAGE_DOWNLOAD_PATH = eval(config.get(STORAGE_CONFIG_SECTION, "image_download_path"))

        self.LOG_FILE_NAME = config.get(LOGS_CONFIG_SECTION, "log_file_name")

        self.MODELS_PATH = config.get(MODELS_CONFIG_SECTION, "models_directory")

        self.JOBS_TIME = eval(config.get(JOBS_CONFIG_SECTION, "jobs_time"))
        self.JOBS_TEST_MODE = eval(config.get(TEST_CONFIG_SECTION, "test_jobs"))
