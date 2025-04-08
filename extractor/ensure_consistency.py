def ensure_consistency(entities, relationships, reference_mappings, threshold=1):
    """
    Ensures consistency between entity types and relationship types using a single threshold.

    For each relationship, check its required entity types (via reference_mappings).
    - If a required entity type is missing and the number of relationships needing that entity is
      greater than or equal to the threshold, then add that entity type to the entity list.
    - Otherwise, remove relationships that require a missing entity.

    Parameters:
      entities: List[str]
          List of entity type strings (e.g., ["CHARACTER", "LOCATION", ...]).
      relationships: List[str]
          List of relationship type strings.
      reference_mappings: dict
          Dictionary mapping relationship names to a dict of required entity references.
          For example:
              {
                "Organization_MEMBER_OF": {
                    "Characters": ("CHARACTER", some_func),
                    "Organizations": ("ORGANIZATION", another_func)
                },
                ...
              }
      threshold: int
          The minimum number of relationships requiring a missing entity type to add it.
          Otherwise, any relationship that requires a missing entity (with count below threshold)
          will be removed.

    Returns:
      (updated_entities, updated_relationships): tuple
          The updated list of entity type strings and relationship type strings.
    """
    # Use a set for fast lookup.
    entities_set = set(entities)

    # First pass: Count missing occurrences for each entity type across all relationships.
    missing_counts = {}
    for rel in relationships:
        reqs = reference_mappings.get(rel, {})
        for key, (req_entity, _) in reqs.items():
            if req_entity not in entities_set:
                missing_counts[req_entity] = missing_counts.get(req_entity, 0) + 1

    # Second pass: Decide whether to keep or remove each relationship.
    updated_relationships = []
    for rel in relationships:
        reqs = reference_mappings.get(rel, {})
        missing_for_rel = []
        for key, (req_entity, _) in reqs.items():
            if req_entity not in entities_set:
                missing_for_rel.append(req_entity)
        # For each missing entity in this relationship, check if its count meets the threshold.
        # If any required entity does not meet the threshold, skip this relationship.
        remove_rel = False
        for missing_entity in missing_for_rel:
            if missing_counts.get(missing_entity, 0) < threshold:
                remove_rel = True
                break
        if remove_rel:
            continue
        # Otherwise, add any missing entity (that meets threshold) to the entities set.
        for missing_entity in missing_for_rel:
            entities_set.add(missing_entity)
        updated_relationships.append(rel)

    updated_entities = list(entities_set)
    return updated_entities, updated_relationships
