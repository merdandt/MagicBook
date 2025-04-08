def extract_edge_ids(rel_type, relationship):
    """Extract source and target IDs from a relationship record based on its type."""
    # Mapping relationship type to a lambda that returns (source_id, target_id)
    extractors = {
        # Family Relationships
        "Family_PARENT_OF": lambda r: (r.get("parent_id"), r.get("child_id")),
        "Family_SIBLING_OF": lambda r: (r.get("sibling1_id"), r.get("sibling2_id")),
        "Family_MARRIED_TO": lambda r: (r.get("spouse1_id"), r.get("spouse2_id")),

        # Emotional Relationships
        "Emotional_LOVES": lambda r: (r.get("lover_id"), r.get("beloved_id")),
        "Emotional_TRUSTS": lambda r: (r.get("truster_id"), r.get("trusted_id")),
        "Emotional_BETRAYED": lambda r: (r.get("betrayer_id"), r.get("betrayed_id")),

        # Interaction Relationships
        "Interaction_INTERACTED_WITH": lambda r: (r.get("character1_id"), r.get("character2_id")),
        "Interaction_APPEARED_TOGETHER": lambda r: (r.get("character1_id"), r.get("character2_id")),
        "Interaction_MET_AT": lambda r: (r.get("character1_id"), r.get("character2_id")),

        # Location Relationships
        "Location_PRESENT_AT": lambda r: (r.get("character_id"), r.get("location_id")),
        "Location_TRAVELED_TO": lambda r: (r.get("character_id"), r.get("location_id")),
        "Location_BATTLE_AT": lambda r: (r.get("event_id"), r.get("location_id")),
        "Location_LIVES_IN": lambda r: (r.get("character_id"), r.get("location_id")),

        # Event Relationships
        "Event_WITNESSED": lambda r: (r.get("character_id"), r.get("event_id")),
        "Event_PARTICIPATED_IN": lambda r: (r.get("character_id"), r.get("event_id")),
        "Event_CAUSED": lambda r: (r.get("character_id"), r.get("event_id")),
        "Event_AFFECTED_BY": lambda r: (r.get("character_id"), r.get("event_id")),
        "Event_BORN_AT": lambda r: (r.get("character_id"), r.get("event_id")),
        "Event_DIED_AT": lambda r: (r.get("character_id"), r.get("event_id")),
        "Event_BEFORE": lambda r: (r.get("earlier_event_id"), r.get("later_event_id")),
        "Event_AFTER": lambda r: (r.get("later_event_id"), r.get("earlier_event_id")),
        "Event_SIMULTANEOUS_WITH": lambda r: (r.get("event1_id"), r.get("event2_id")),
        "Event_OVERLAPS_WITH": lambda r: (r.get("event1_id"), r.get("event2_id")),
        "Event_CAUSES": lambda r: (r.get("cause_event_id"), r.get("effect_event_id")),
        "Event_CAUSED_BY": lambda r: (r.get("effect_event_id"), r.get("cause_event_id")),

        # Organization Relationships
        "Organization_MEMBER_OF": lambda r: (r.get("character_id"), r.get("organization_id")),
        "Organization_LEADER_OF": lambda r: (r.get("character_id"), r.get("organization_id")),
        "Organization_FOUNDED_BY": lambda r: (r.get("organization_id"), r.get("founder_id")),

        # Creature Relationships
        "Creature_BELONGS_TO_SPECIES": lambda r: (r.get("character_id"), r.get("creature_id")),
        "Creature_CONTROLLED_BY": lambda r: (r.get("creature_id"), r.get("controller_id")),
        "Creature_ALLIED_WITH": lambda r: (r.get("creature1_id"), r.get("creature2_id")),

        # Conceptual Relationships
        "Concept_HAS_ABILITY": lambda r: (r.get("character_id"), r.get("concept_id")),
        "Concept_BELIEVES_IN": lambda r: (r.get("character_id"), r.get("concept_id")),
        "Concept_RESISTS": lambda r: (r.get("character_id"), r.get("concept_id")),
        "Concept_INFLUENCED_BY": lambda r: (r.get("character_id"), r.get("concept_id")),

        # Item Relationships
        "Item_POSSESSES": lambda r: (r.get("character_id"), r.get("item_id")),
        "Item_CREATED": lambda r: (r.get("character_id"), r.get("item_id")),
        "Item_SEEKS": lambda r: (r.get("character_id"), r.get("item_id")),
        "Item_DESTROYED": lambda r: (r.get("character_id"), r.get("item_id")),
        "Item_USED_IN": lambda r: (r.get("item_id"), r.get("event_id")),

        # Item-Item Relationships
        "ItemItem_COMPONENT_OF": lambda r: (r.get("component_id"), r.get("whole_id")),
        "ItemItem_COUNTERS": lambda r: (r.get("item1_id"), r.get("item2_id")),

        # Item-Location Relationships
        "ItemLocation_LOCATED_AT": lambda r: (r.get("item_id"), r.get("location_id")),
        "ItemLocation_ORIGINATED_FROM": lambda r: (r.get("item_id"), r.get("origin_location_id")),
    }

    extractor = extractors.get(rel_type)
    if extractor:
        return extractor(relationship)

    # For unrecognized relationships, try to return the first two keys ending with '_id'
    id_keys = [k for k in relationship if k.endswith("_id")]
    if len(id_keys) >= 2:
        return relationship.get(id_keys[0]), relationship.get(id_keys[1])

    return None, None