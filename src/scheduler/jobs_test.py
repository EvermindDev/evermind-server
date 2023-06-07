import json
import os
import shutil
from datetime import datetime, timedelta
import random


class JobsTest:
    def __init__(self, config):
        self.config = config

    def run(self):
        self.process_open_prompts()

    def process_open_prompts(self):
        prompts_directory = 'data/prompts'
        image_directory = 'data/images'

        for filename in os.listdir(prompts_directory):
            if filename.endswith('.json'):
                filepath = os.path.join(prompts_directory, filename)
                with open(filepath, 'r') as file:
                    prompt_data = json.load(file)

                if prompt_data.get('status') == 'OPEN' or prompt_data.get('status') == 'COMPLETED':
                    self.process_prompt(filename, filepath, prompt_data, image_directory)

    def process_prompt(self, filename, filepath, prompt_data, image_directory):
        prompt_id = os.path.splitext(filename)[0]
        prompt_date = datetime.strptime(prompt_data.get('prompt_date'), '%Y-%m-%d %H:%M')
        x_hours_ago = datetime.now() - timedelta(hours=2)

        if prompt_date < x_hours_ago:
            self.delete_prompt(filepath, prompt_id, prompt_data, image_directory)
        else:
            self.process_open_prompt(prompt_id, filepath, prompt_data, image_directory)

    def delete_prompt(self, filepath, prompt_id, prompt_data, image_directory):
        os.remove(filepath)

        # Delete associated images from data/images directory
        image_list = prompt_data.get('output', [])
        for image in image_list:
            image_filename = image.get('name')
            if image_filename:
                image_path = os.path.join(image_directory, image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)

    def process_open_prompt(self, prompt_id, filepath, prompt_data, image_directory):

        # Update the prompt status to 'COMPLETED'
        prompt_data['status'] = 'COMPLETED'

        # Add the image list to the output
        image_list = []
        os.makedirs(image_directory, exist_ok=True)

        test_images_dir = 'data/test-images'
        test_images = os.listdir(test_images_dir)

        if test_images:
            for i in range(4):
                # Get a random image filename from the test images directory
                image_filename = random.choice(test_images)
                image_path = os.path.join(image_directory, image_filename)
                shutil.copyfile(os.path.join(test_images_dir, image_filename), image_path)

                image_url = f"{self.config.APP_URL}:{self.config.APP_PORT}" \
                            f"{self.config.IMAGE_DOWNLOAD_PATH}{image_filename}" \
                    if self.config.APP_PORT else f"{self.config.APP_URL}" \
                                                 f"{self.config.IMAGE_DOWNLOAD_PATH}{image_filename}"

                image_list.append({'image': image_url, 'name': image_filename})

            prompt_data['output'] = image_list

            with open(filepath, 'w') as file:
                json.dump(prompt_data, file)
        else:
            print(f"No available images in the test-images directory for prompt: {prompt_id}")
