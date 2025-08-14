import json
import re
import yaml

def clean_text(text):
    if text is None:
        return ""
    # Remove HTML tags
    cleaned = re.sub(r'<[^>]+>', '', text)
    # Replace multiple spaces with a single space and trim
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def process_data(input_json_path, output_yaml_path):
    with open(input_json_path, 'r') as f:
        raw_data = json.load(f)

    processed_data = []
    for item in raw_data['tbody']['tr']:
        switch_id = item.get('+@id')

        raw_switch_obj = item['td'][0]
        
        switch_name = ""
        if isinstance(raw_switch_obj, dict):
            switch_name = clean_text(raw_switch_obj.get('+content'))
        elif isinstance(raw_switch_obj, str):
            switch_name = clean_text(raw_switch_obj)
        
        # Remove the '⊗' character and any leading/trailing whitespace around it
        switch_name = re.sub(r'\s*⊗', '', switch_name).strip()


        description = ""
        raw_description_obj = item['td'][1]

        if isinstance(raw_description_obj, dict):
            if raw_description_obj.get('i') == "No description":
                description = "No description provided."
            elif raw_description_obj.get('+content'):
                description = clean_text(raw_description_obj.get('+content'))
                if not description:
                    description = "No description provided."
            else:
                description = "No description provided."
        elif isinstance(raw_description_obj, str):
            description = clean_text(raw_description_obj)
            if not description:
                description = "No description provided."
        else:
            description = "No description provided."

        source_url = None
        if isinstance(raw_description_obj, dict) and 'a' in raw_description_obj:
            if isinstance(raw_description_obj['a'], dict):
                source_url = raw_description_obj['a'].get('+@href')
            elif isinstance(raw_description_obj['a'], list):
                for a_tag in raw_description_obj['a']:
                    if isinstance(a_tag, dict) and a_tag.get('+content') == '↪':
                        source_url = a_tag.get('+@href')
                        break

        processed_item = {
            "id": switch_id,
            "switch": switch_name,
            "description": description,
            "source_url": source_url
        }
        processed_data.append(processed_item)

    with open(output_yaml_path, 'w') as f:
        yaml.dump(processed_data, f, sort_keys=False, indent=2, default_flow_style=False, allow_unicode=True)

input_json_path = "/home/colton/git/chrome-switches.github.io/_data/raw_switches.json"
output_yaml_path = "/home/colton/git/chrome-switches.github.io/_data/switches.yaml"
process_data(input_json_path, output_yaml_path)