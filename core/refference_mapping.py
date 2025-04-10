def reference_mapping_creator():
    # Define common entity property extractors
    character_basic = lambda c: {"_key": c["_key"], "name": c["name"]}
    character_standard = lambda c: {**character_basic(c), "significance": c.get("significance", "")}
    character_detailed = lambda c: {**character_standard(c), "gender": c.get("gender", "")}
    character_professional = lambda c: {**character_basic(c), "occupation": c.get("occupation", ""), "status": c.get("status", "")}
    character_descriptive = lambda c: {**character_basic(c), "description": c.get("description", "")}

    location_basic = lambda l: {"_key": l["_key"], "name": l["name"]}
    location_typed = lambda l: {**location_basic(l), "type": l.get("type", "")}
    location_detailed = lambda l: {**location_typed(l), "significance": l.get("significance", "")}
    location_regional = lambda l: {**location_typed(l), "region": l.get("region", "")}

    event_basic = lambda e: {"_key": e["_key"], "name": e["name"]}
    event_typed = lambda e: {**event_basic(e), "type": e.get("type", "")}
    event_detailed = lambda e: {**event_typed(e), "summary": e.get("summary", "")}

    item_basic = lambda i: {"_key": i["_key"], "name": i["name"]}
    item_typed = lambda i: {**item_basic(i), "type": i.get("type", "")}
    item_status = lambda i: {**item_basic(i), "current_status": i.get("current_status", "")}
    item_detailed = lambda i: {**item_typed(i), "description": i.get("description", "")}
    item_magical = lambda i: {**item_typed(i), "magical": i.get("magical", False)}
    item_origin = lambda i: {**item_typed(i), "origin": i.get("origin", "")}

    # For TIME_PERIOD, add a basic extractor:
    timeperiod_basic = lambda tp: {"_key": tp["_key"], "name": tp["name"]}
    timeperiod_detailed = lambda tp: {**timeperiod_basic(tp), "description": tp.get("description", "")}

    # Group relationships by common entity requirements
    reference_mappings = {
        # Character-Character relationships
        key: {"Characters": ("CHARACTER", character_detailed)}
        for key in ["Family_PARENT_OF", "Family_SIBLING_OF", "Family_MARRIED_TO",
                    "Emotional_LOVES", "Emotional_TRUSTS", "Emotional_BETRAYED"]
    }

    # Add interaction relationships
    reference_mappings.update({
        key: {"Characters": ("CHARACTER", character_standard)}
        for key in ["Interaction_INTERACTED_WITH", "Interaction_APPEARED_TOGETHER"]
    })

    # Add complex relationships
    reference_mappings.update({
        "Interaction_MET_AT": {
            "Characters": ("CHARACTER", character_standard),
            "Locations": ("LOCATION", location_typed),
            "Events": ("EVENT", event_typed)
        },

        # Location relationships
        "Location_PRESENT_AT": {
            "Characters": ("CHARACTER", character_standard),
            "Locations": ("LOCATION", location_detailed)
        },
        "Location_TRAVELED_TO": {
            "Characters": ("CHARACTER", character_standard),
            "Locations": ("LOCATION", location_typed)
        },
        "Location_BATTLE_AT": {
            "Events": ("EVENT", event_typed),
            "Locations": ("LOCATION", location_typed)
        },
        "Location_LIVES_IN": {
            "Characters": ("CHARACTER", character_standard),
            "Locations": ("LOCATION", location_typed)
        },

        # Event relationships
        "Event_WITNESSED": {
            "Characters": ("CHARACTER", character_standard),
            "Events": ("EVENT", event_detailed)
        },
        "Event_PARTICIPATED_IN": {
            "Characters": ("CHARACTER", character_standard),
            "Events": ("EVENT", event_detailed)
        },
        "Event_CAUSED": {
            "Characters": ("CHARACTER", character_standard),
            "Events": ("EVENT", event_detailed)
        },
        "Event_AFFECTED_BY": {
            "Characters": ("CHARACTER", character_standard),
            "Events": ("EVENT", event_detailed)
        },
        "Event_BORN_AT": {
            "Characters": ("CHARACTER", lambda c: {**character_basic(c), "age": c.get("age", "")}),
            "Events": ("EVENT", event_typed)
        },
        "Event_DIED_AT": {
            "Characters": ("CHARACTER", lambda c: {**character_basic(c), "alive": c.get("alive", True)}),
            "Events": ("EVENT", event_typed)
        },

        # Organization relationships
        "Organization_MEMBER_OF": {
            "Characters": ("CHARACTER", character_professional),
            "Organizations": ("ORGANIZATION", lambda o: {"_key": o["_key"], "name": o["name"]})
        },
        "Organization_LEADER_OF": {
            "Characters": ("CHARACTER", character_professional),
            "Organizations": ("ORGANIZATION", lambda o: {"_key": o["_key"], "name": o["name"]})
        },
        "Organization_FOUNDED_BY": {
            "Characters": ("CHARACTER", character_standard),
            "Organizations": ("ORGANIZATION", lambda o: {"_key": o["_key"], "name": o["name"]})
        },

        # Creature relationships
        "Creature_BELONGS_TO_SPECIES": {
            "Characters": ("CHARACTER", character_descriptive),
            "Creatures": ("CREATURE", lambda cr: {"_key": cr["_key"], "name": cr["name"]})
        },
        "Creature_CONTROLLED_BY": {
            "Creatures": ("CREATURE", lambda cr: {"_key": cr["_key"], "name": cr["name"]}),
            "Characters": ("CHARACTER", character_standard)
        },
        "Creature_ALLIED_WITH": {
            "Creatures": ("CREATURE", lambda cr: {"_key": cr["_key"], "name": cr["name"]}),
            "Characters": ("CHARACTER", character_standard)
        },

        # Concept relationships
        "Concept_HAS_ABILITY": {
            "Characters": ("CHARACTER", character_descriptive),
            "Concepts": ("CONCEPT", lambda cn: {"_key": cn["_key"], "name": cn["name"]})
        },
        "Concept_BELIEVES_IN": {
            "Characters": ("CHARACTER", character_descriptive),
            "Concepts": ("CONCEPT", lambda cn: {"_key": cn["_key"], "name": cn["name"]})
        },
        "Concept_RESISTS": {
            "Characters": ("CHARACTER", character_descriptive),
            "Concepts": ("CONCEPT", lambda cn: {"_key": cn["_key"], "name": cn["name"]})
        },
        "Concept_INFLUENCED_BY": {
            "Characters": ("CHARACTER", character_descriptive),
            "Concepts": ("CONCEPT", lambda cn: {"_key": cn["_key"], "name": cn["name"]})
        }
    })

    # Temporal relationships
    reference_mappings.update({
        key: {"Events": ("EVENT", event_detailed)}
        for key in ["Event_BEFORE", "Event_AFTER", "Event_SIMULTANEOUS_WITH",
                    "Event_OVERLAPS_WITH", "Event_CAUSES", "Event_CAUSED_BY"]
    })

    # Item relationships
    reference_mappings.update({
        "Item_POSSESSES": {
            "Characters": ("CHARACTER", character_standard),
            "Items": ("ITEM", lambda i: {**item_typed(i), "magical": i.get("magical", False), "current_status": i.get("current_status", "")})
        },
        "Item_CREATED": {
            "Characters": ("CHARACTER", character_professional),
            "Items": ("ITEM", item_origin)
        },
        "Item_SEEKS": {
            "Characters": ("CHARACTER", character_standard),
            "Items": ("ITEM", item_detailed)
        },
        "Item_DESTROYED": {
            "Characters": ("CHARACTER", character_standard),
            "Items": ("ITEM", item_status)
        },
        "Item_USED_IN": {
            "Characters": ("CHARACTER", character_standard),
            "Items": ("ITEM", item_typed)
        },

        # Item-Item Relationships
        "ItemItem_COMPONENT_OF": {
            "Items": ("ITEM", item_detailed)
        },
        "ItemItem_COUNTERS": {
            "Items": ("ITEM", lambda i: {**item_detailed(i), "magical": i.get("magical", False)})
        },

        # Item-Location Relationships
        "ItemLocation_LOCATED_AT": {
            "Items": ("ITEM", lambda i: {**item_typed(i), "current_status": i.get("current_status", "")}),
            "Locations": ("LOCATION", location_typed)
        },
        "ItemLocation_ORIGINATED_FROM": {
            "Items": ("ITEM", item_origin),
            "Locations": ("LOCATION", location_regional)
        }
    })

    # Optionally, add a temporal relationship that involves TIME_PERIOD.
    reference_mappings.update({
        "Event_OCCURS_DURING": {
            "Events": ("EVENT", event_detailed),
            "TimePeriods": ("TIME_PERIOD", timeperiod_detailed)
        }
    })
    
    return reference_mappings
