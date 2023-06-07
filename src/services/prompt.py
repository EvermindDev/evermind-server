import json
import os
import uuid
from datetime import datetime

from flask import jsonify, request


class Prompt:

    def __init__(self, config):
        self.config = config

    def create_prompt(self):
        new_prompt = request.json
        print(new_prompt)
        prompts_directory = 'data/prompts'
        os.makedirs(prompts_directory, exist_ok=True)
        data_uuid = str(uuid.uuid4())
        filename = os.path.join(prompts_directory, data_uuid + '.json')

        new_prompt['status'] = 'OPEN'
        new_prompt['prompt_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')

        # Extract model_id from the route
        model_id = request.path.split('/')[2]
        new_prompt['model_id'] = model_id

        with open(filename, 'w') as file:
            json.dump(new_prompt, file)

        response = {
            'status': new_prompt['status'],
            'id': data_uuid
        }

        return jsonify(response), 201

    def get_prompt(self, prompt_uuid):
        prompts_directory = 'data/prompts'
        filename = os.path.join(prompts_directory, prompt_uuid + '.json')

        try:
            with open(filename, 'r') as file:
                prompt_data = json.load(file)

            response = {
                'status': prompt_data['status'],
                'id': prompt_uuid
            }

            if 'output' in prompt_data:
                response['output'] = prompt_data['output']
            else:
                response['output'] = []

        except FileNotFoundError:
            response = {
                'status': 'NOT_FOUND',
                'id': prompt_uuid
            }

        return jsonify(response), 201
