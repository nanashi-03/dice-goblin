from db import characters, users

def get_active_character(user):
    user_id = str(user)
    user_doc = users.find_one({"user_id": user_id})
    if not user_doc or not user_doc.get("current_character"):
        return None
    
    pb_id = user_doc["current_character"]
    character = characters.find_one({"user_id": user_id, "pb_id": pb_id})
    if not character:
        return None
    return character
