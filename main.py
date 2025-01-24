from module import (
    get_pages,
    safe_get_property,
    get_database_schema,
    add_page_to_database,
)

NOTION_TOKEN = 'your_notion_token'
TRANSACTION_DB_ID = 'your_transaction_db_id'
SHIFT_BALANCE_DB_ID = "your_shift_balance_db_id"

def main_task():
    # Your existing code for automating the task
    column_dict = {}
    pages = get_pages(TRANSACTION_DB_ID)

    # Process pages and extract relevant data
    for page in pages:
        props = page["properties"]
        column_dict[page["id"]] = {
            "Legendary_Member": safe_get_property(props, "Legendary_Member", "select"),
            "IN/OUT": safe_get_property(props, "IN/OUT", "select"),
            "Amount": safe_get_property(props, "Amount", "number"),
            "Account": safe_get_property(props, "Account", "select"),
            "Date": safe_get_property(props, "Date", "date"),
        }

    # Calculate net amounts
    net_amounts = {}
    for properties in column_dict.values():
        account = properties.get("Account")
        if not account:
            continue

        net_amounts[account] = net_amounts.get(account, 0) + (
            properties["Amount"] if properties["IN/OUT"] == "IN" else -properties["Amount"]
        )

    # Ensure all accounts from the schema are accounted for
    schema = get_database_schema(TRANSACTION_DB_ID)
    if schema:
        account_options = [
            opt["name"]
            for opt in schema.get("properties", {}).get("Account", {}).get("select", {}).get("options", [])
        ]
        net_amounts.update({acc: net_amounts.get(acc, 0) for acc in account_options})

    # Add data to the second database
    operator_name = column_dict[next(iter(column_dict), {})].get("Legendary_Member")
    add_page_to_database(SHIFT_BALANCE_DB_ID, net_amounts, operator_name)

    return "Task completed"
