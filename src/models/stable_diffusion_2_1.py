import json
import os
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from flask import jsonify


class StableDiffusion21:
    def __init__(self, config):
        self.config = config

    def run_model(self, prompt_uuid, prompt, negative_prompt, width, height, guidance_scale, num_inference_steps,
                  num_outputs, prompt_strength, scheduler, model_id, device):
        kwargs = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps
        }

        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        pipe = pipe.to(device)

        output = pipe(**kwargs)
        images = output.images
        image_urls = []

        for i, image in enumerate(images):
            image = image.convert("RGB")  # Convert to RGB mode if needed
            image_filename = f"{prompt_uuid}_{i}.png"
            image_path = os.path.join(self.config.IMAGE_STORAGE, image_filename)
            image.save(image_path)
            image_url = f"{self.config.APP_URL}:{self.config.APP_PORT}" \
                        f"{self.config.IMAGE_DOWNLOAD_PATH}{image_filename}" \
                if self.config.APP_PORT else f"{self.config.APP_URL}" \
                                             f"{self.config.IMAGE_DOWNLOAD_PATH}{image_filename}"
            image_urls.append({'image': image_url, 'name': image_filename})

        return image_urls

    def run(self, prompt_uuid):
        model_id = "stabilityai/stable-diffusion-2-1"

        # Get prompt by prompt_uuid and open the prompt JSON file
        prompts_directory = 'data/prompts'
        filename = os.path.join(prompts_directory, prompt_uuid + '.json')

        try:
            with open(filename, 'r') as file:
                prompt_data = json.load(file)

            prompt = prompt_data['input']['prompt']
            negative_prompt = prompt_data['input'].get('negative_prompt', '')
            width = prompt_data['input'].get('width', 512)
            height = prompt_data['input'].get('height', 512)
            guidance_scale = prompt_data['input'].get('guidance_scale', 7.5)
            num_inference_steps = prompt_data['input'].get('num_inference_steps', 50)
            num_outputs = prompt_data['input'].get('num_outputs', 1)
            prompt_strength = prompt_data['input'].get('prompt_strength', 0.8)
            scheduler = prompt_data['input'].get('scheduler', 'K-LMS')

            # Run the model with the prompt
            device = "cuda" if torch.cuda.is_available() else "cpu"
            output_images = self.run_model(
                prompt_uuid,
                prompt,
                negative_prompt,
                width,
                height,
                guidance_scale,
                num_inference_steps,
                num_outputs,
                prompt_strength,
                scheduler,
                model_id,
                device
            )

            # Update prompt_data with the output images and status
            prompt_data['status'] = 'COMPLETED'
            prompt_data['output'] = output_images

            # Save the updated prompt_data to the JSON file
            with open(filename, 'w') as file:
                json.dump(prompt_data, file)

            # Generate the JSON response
            response = {
                'input': prompt_data['input'],
                'status': prompt_data['status'],
                'prompt_date': prompt_data['prompt_date'],
                'model_id': model_id,
                'output': output_images
            }

            print(response)

            return jsonify(response), 200

        except FileNotFoundError:
            # Handle the case when the prompt file is not found
            response = {
                'status': 'NOT_FOUND',
                'id': prompt_uuid
            }
            return jsonify(response), 404
