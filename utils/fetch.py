from db import characters

def get_active_character(user):
    user_id = str(user)
    return characters.find_one({"user_id": user_id})
