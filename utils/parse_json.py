from datetime import datetime, timezone
def parse_pathbuilder_character(user_id, data, pid):
    build = data["build"]

    skill_to_ability = {
        "acrobatics": "dex",
        "arcana": "int",
        "athletics": "str",
        "crafting": "int",
        "deception": "cha",
        "diplomacy": "cha",
        "intimidation": "cha",
        "medicine": "wis",
        "nature": "wis",
        "occultism": "int",
        "performance": "cha",
        "religion": "wis",
        "society": "int",
        "stealth": "dex",
        "survival": "wis",
        "thievery": "dex"
    }

    # Extract abilities
    abilities = build["abilities"]
    scores = {k: int((abilities[k] - 10) / 2) for k in ["str", "dex", "con", "int", "wis", "cha"]}

    level = build.get("level")
    key_ability = build.get("keyability")

    # Extract skills from proficiencies (any with value >= 1)
    profs = build["proficiencies"]

    # skills = {skill: profs.get(skill, 0) for skill in [
    #     "acrobatics", "arcana", "athletics", "crafting", "deception",
    #     "diplomacy", "intimidation", "medicine", "nature", "occultism",
    #     "performance", "religion", "society", "stealth", "survival", "thievery"
    # ]}
    skills = {}
    for skill, ability in skill_to_ability.items():
        prof = profs.get(skill, 0)
        if prof > 0:
            bonus = level + prof
        else:
            bonus = 0
        ability_mod = scores[ability]
        skills[skill] = ability_mod + bonus

    def get_spellcasters(casters):
        return [
            {
                "tradition": c.get("tradition"),
                "type": c.get("type"),
                "focusPoints": c.get("focusPoints", 0),
                "spells": c.get("spells", {})
            }
            for c in casters
        ]

    def get_pets(pets):
        return [
            {
                "name": p.get("name"),
                "type": p.get("type"),
                "animal": p.get("animal"),
                "mature": p.get("mature"),
                "armor": p.get("armor")
            }
            for p in pets
        ]

    # Flatten feat names
    feats = [f"{f[0]} ({f[1]})" if f[1] else f[0] for f in build["feats"]]

    # Flatten equipment names
    equipment = [item[0] for item in build["equipment"]]
    
    weapons_raw = build.get("weapons", [])
    weapons = []

    for w in weapons_raw:
        weapons.append({
            "name": w.get("name"),
            "display": w.get("display"),
            "attack_bonus": w.get("attack", 0),
            "damage_die": w.get("die"),
            "damage_type": w.get("damageType"),
            "damage_bonus": w.get("damageBonus", 0),
            "proficiency": w.get("prof", "simple"),
            "potency": w.get("pot", 0),
            "striking": w.get("str", 0),
            "runes": w.get("runes", []),  # Optional
        })

    armor = [a["name"] for a in build.get("armor", [])]
    lores = {name.lower(): (level + prof + scores["int"]) for name, prof in build.get("lores", [])}

    saves = {
        "fortitude": level + profs.get("fortitude", 0) + scores["con"],
        "reflex": level + profs.get("reflex", 0) + scores["dex"],
        "will": level + profs.get("will", 0) + scores["wis"],
    }

    return {
        "user_id": user_id,
        "pb_id": pid,
        "name": build.get("name"),
        "class": build.get("class"),
        "key_ability": key_ability,
        "classDC": 10 + scores[key_ability] + level + profs.get("classDC", 0),
        "level": level,
        "ancestry": build.get("ancestry"),
        "heritage": build.get("heritage"),
        "background": build.get("background"),
        "size": build.get("sizeName"),
        "languages": build.get("languages", []),
        "resistances": build.get("resistances", []),
        "abilities": scores,
        "saves": saves,
        "perception": level + profs.get("perception", 0) + scores["wis"],
        "skills": skills,
        "lores": lores,
        "feats": feats,
        "equipment": equipment,
        "weapons": weapons,
        "armor": armor,
        "hp": build["attributes"]["ancestryhp"] + (build["attributes"]["classhp"] + scores["con"]) * level,
        "speed": build["attributes"]["speed"] + build["attributes"].get("speedBonus", 0),
        "ac": build.get("acTotal", {}).get("acTotal", 10),
        "specials": build.get("specials", []),
        "focus": build.get("focus", {}),
        "formula": build.get("formula", []),
        "spellcasters": get_spellcasters(build.get("spellCasters", [])),
        "focusPoints": build.get("focusPoints", 0),
        "pets": get_pets(build.get("pets", [])),
        "familiars": build.get("familiars", []),
        "money": build.get("money", {}),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
