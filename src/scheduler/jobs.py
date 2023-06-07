import json
import os
import shutil
from datetime import datetime, timedelta
import random
from src.models.stable_diffusion_2_1 import StableDiffusion21


class Jobs:
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

        if prompt_data.get('status') == 'COMPLETED' and prompt_date < x_hours_ago:
            self.delete_prompt(filepath, prompt_id, prompt_data, image_directory)
        else:
            if prompt_data.get('status') == 'OPEN':
                self.process_open_prompt(prompt_id, filepath, prompt_data, image_directory)
            else:
                pass

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
        model_id = prompt_data.get('model_id')

        if model_id == 'stable-diffusion-2-1':
            # Run the StableDiffusion21 model
            stable_diffusion = StableDiffusion21(self.config)
            response, status_code = stable_diffusion.run(prompt_id)

            if status_code == 200:
                pass
            else:
                print(f"Error running StableDiffusion21 model for prompt: {prompt_id}")
        else:
            print(f"Model ID {model_id} not supported for prompt: {prompt_id}")
