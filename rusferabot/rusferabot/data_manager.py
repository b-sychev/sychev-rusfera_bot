import json
import os
from datetime import datetime
from typing import Dict, List, Optional

DATA_FILE = "data/requests.json"

def ensure_data_dir():
    os.makedirs("data", exist_ok=True)

def load_requests() -> Dict[str, Dict]:
    ensure_data_dir()
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_requests(requests: Dict[str, Dict]):
    ensure_data_dir()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(requests, f, indent=2, ensure_ascii=False, default=str)

def add_request(request_data: Dict) -> str:
    requests = load_requests()
    request_number = request_data['number']
    requests[request_number] = request_data
    save_requests(requests)
    return request_number

def get_request(request_number: str) -> Optional[Dict]:
    requests = load_requests()
    return requests.get(request_number)

def get_all_requests() -> List[Dict]:
    requests = load_requests()
    return list(requests.values())

def update_request_status(request_number: str, new_status: str):
    requests = load_requests()
    if request_number in requests:
        requests[request_number]['status'] = new_status
        save_requests(requests)