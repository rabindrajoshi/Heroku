from datetime import datetime, timezone
import requests

NOTION_TOKEN= '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'

HEADERS  = {
    "Authorization": "Bearer "+ NOTION_TOKEN,
    "Notion-Version": "2022-06-28",
    "content-type": "application/json"

}

def format_date(date_string):
    try:
        return datetime.fromisoformat(date_string.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    

def get_pages(database_id, num_pages=None):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = {"page_size": num_pages or 100}
    results = []

    while True:
        response = requests.post(url, json=payload, headers=HEADERS).json()
        results.extend(response["results"])
        if not response.get("has_more"):
            break
        payload["start_cursor"] = response["next_cursor"]

    return results

def safe_get_property(properties, key, prop_type):
    try:
        value = properties[key].get(prop_type)
        if prop_type in ["title", "rich_text"]:
            return value[0]["text"]["content"] if value else None
        elif prop_type == "select":
            return value["name"] if value else None
        elif prop_type == "number":
            return value or 0
        elif prop_type == "date":
            return format_date(value["start"])
    except (KeyError, IndexError, TypeError):
        pass
    return None


def get_database_schema(database_id):
    response = requests.get(f"https://api.notion.com/v1/databases/{database_id}", headers=HEADERS)
    return response.json() if response.status_code == 200 else None

def get_database_columns(database_id):
    """
    Retrieve the column names of a Notion database.
    """
    url = f"https://api.notion.com/v1/databases/{database_id}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        database = response.json()
        properties = database.get("properties", {})
        return list(properties.keys())
    else:
        print(f"Failed to retrieve database columns: {response.status_code}, {response.json()}")
        return []

def add_page_to_database(database_id, data_dict, operator_name):
    """
    Create a new page in the database using values from `data_dict` and `operator_name`.
    """
    url = "https://api.notion.com/v1/pages"

    # Build properties payload
    properties = {
        column: {"number": data_dict[column]} if column in data_dict else {
            "rich_text": [{"text": {"content": operator_name}}]
        } 
        for column in get_database_columns(database_id) if column in data_dict or column == "Operator Name"
    }

    # Create the payload and make the request
    payload = {"parent": {"database_id": database_id}, "properties": properties}
    response = requests.post(url, json=payload, headers=HEADERS)

    # Log the response
    print(f"Response: {response.status_code}, {response.text}")
