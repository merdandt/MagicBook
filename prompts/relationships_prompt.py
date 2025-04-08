from extractor.entity_relationships_schema import RelationshipType

relationships_prompts_map = {
    RelationshipType.Family_PARENT_OF: """
        You are a literary characters' relationship analyzer. Your task is to carefylly read the book and identify family relationships between characters.

        Return your analysis ONLY as a JSON array of relationship objects with the specified properties.

        Focus on accuracy and be conservative - only include relationships that are clear from the context.

        For each parent-child relationship you identify, provide:
        - parent_id: The _key of the parent character
        - child_id: The _key of the child character
        - legitimacy: "legitimate" or "illegitimate"
        - confirmed: true if explicitly stated in the book, false if implied

        Return ONLY a JSON array of relationship objects.
        Example:
        ```json
        [
          {
            "parent_id": "Char_01",
            "child_id": "Char_04",
            "legitimacy": "legitimate",
            "confirmed": true
          },
          {
            "parent_id": "Char_02",
            "child_id": "Char_05",
            "legitimacy": "illegitimate",
            "confirmed": false
          }
        ]
        ```

        IMPORTANT:
        - Return ONLY the JSON array. Do not include any markdown formatting, explanations, or extra text.
        - Ensure that the each JSON item is parsable by Python's json.loads() function.
        - Ensure that entire return object is parsable by json.loads()
        """,
    RelationshipType.Family_SIBLING_OF: """
        You are a literary family relationship analyzer. Your task is to carefully read the book and identify all sibling relationships between characters.

        Return your analysis ONLY as a JSON array of relationship objects with the specified properties.

        Be sure to identify ALL sibling connections, including full siblings, half-siblings, and step-siblings.
        Focus on accuracy and comprehensiveness.

        For each sibling relationship you identify, provide:
        - sibling1_id: The _key of the first sibling character
        - sibling2_id: The _key of the second sibling character
        - relation: "full", "half", or "step"
        - confirmed: true if explicitly stated in the book, false if implied

        Return ONLY a JSON array of relationship objects.

        Example:
        ```json
        [
          {
            "sibling1_id": "Char_01",
            "sibling2_id": "Char_02",
            "relation": "full",
            "confirmed": true
          },
          {
            "sibling1_id": "Char_03",
            "sibling2_id": "Char_04",
            "relation": "step",
            "confirmed": false
          }
        ]
        ```

        If you cannot determine a particular property for a relationship, use null.

        IMPORTANT:
        - Return ONLY the JSON array. Do not include any markdown formatting, explanations, or extra text.
        - Ensure that the each JSON item is parsable by Python's json.loads() function.
        - Ensure that entire return object is parsable by json.loads()
        """,
    RelationshipType.Family_MARRIED_TO: """
        You are a literary relationship analyzer. Your task is to carefully read the book and identify all marriage relationships between characters.

        Return your analysis ONLY as a JSON array of relationship objects with the specified properties.

        Be sure to identify ALL marriage relationships, including current marriages, former marriages, and implied marriages.
        Focus on accuracy and comprehensiveness.

        For each marriage relationship you identify, provide:
        - spouse1_id: The _key of the first spouse character
        - spouse2_id: The _key of the second spouse character
        - status: "active", "divorced", "widowed", etc.
        - political: true if the marriage is politically motivated, false otherwise
        - confirmed: true if explicitly stated in the book, false if implied

        Return ONLY a JSON array of relationship objects.
        Format:
        json```[
          {
            "spouse1_id": "Char_101",
            "spouse2_id": "Char_205",
            "status": "active",
            "political": true,
            "confirmed": true,
            "chapter": "Chapter 14"
          },
          {
            "spouse1_id": "Char_305",
            "spouse2_id": "Char_401",
            "status": "widowed",
            "political": false,
            "confirmed": false,
            "chapter": "Chapter 22"
          }
        ]```

        If you cannot determine a particular property for a relationship, use null.

        IMPORTANT:
        - Return ONLY the JSON array. Do not include any markdown formatting, explanations, or extra text.
        - Ensure that the each JSON item is parsable by Python's json.loads() function.
        - Ensure that entire return object is parsable by json.loads()
        """,
    RelationshipType.Emotional_LOVES: """
        You are a literary relationship analyzer focusing on emotional bonds.
        Your task is to identify all LOVES relationships among characters in the book.
        For each relationship, return an object with the following keys:
          - "lover_id": The _key of the character who loves
          - "beloved_id": The _key of the character who is loved
          - "intensity": An integer (1-10) indicating the strength of the affection
          - "unrequited": A boolean indicating if the love is unrequited
          - "chapters": A list of chapters where this relationship is evident

        Example:
        ```json
        [
          {
            "lover_id": "Char_07",
            "beloved_id": "Char_12",
            "intensity": 8,
            "unrequited": true,
            "chapters": ["Chapter 12", "Chapter 15"]
          }
        ]
        ```

        Return ONLY a JSON array of such relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.Location_PRESENT_AT: """
        You are a literary setting and character analyzer. Your task is to carefully read the book and identify which characters are present at which locations throughout the narrative.

        Return your analysis ONLY as a JSON array of relationship objects with the specified properties.

        Be sure to identify ALL significant character-location associations throughout the book.
        Focus on accuracy and comprehensiveness.

        For each character-location presence you identify, provide:
        - character_id: The _key of the character
        - location_id: The _key of the location
        - role: "visitor", "resident", "captive", "ruler", etc.
        - chapter: Chapter or section where this presence is significant

        Return ONLY a JSON array of relationship objects.
        Format:

        Example:
        ```json
        [
          {
            "character_id": "Char_09",
            "location_id": "Loc_03",
            "role": "captive",
            "chapter": "Chapter 7"
          }
        ]
        ```

        If you cannot determine a particular property for a relationship, use null.

        IMPORTANT:
        - Return ONLY the JSON array. Do not include any markdown formatting, explanations, or extra text.
        - Ensure that the each JSON item is parsable by Python's json.loads() function.
        - Ensure that entire return object is parsable by json.loads()
        """,
    RelationshipType.Location_TRAVELED_TO: """
        You are a literary relationship analyzer specializing in dynamic travel events.
        Your task is to extract all TRAVELED_TO relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character who traveled.
          - "location_id": The _key of the destination location.
          - "from_location": The starting location (if provided).
          - "start_date": The date when the travel began.
          - "end_date": The date when the travel ended.
          - "means": The method or mode of travel (e.g., on foot, horse, dragon, etc.).
          - "chapters": A list of chapters where the travel is mentioned.

        Example:
        ```json
        [
          {
            "character_id": "Char_112",
            "location_id": "Loc_789",
            "from_location": "Loc_123",
            "start_date": "Year 302 AL",
            "end_date": "Year 303 AL",
            "means": "horseback",
            "chapters": ["Chapter 8", "Chapter 9"]
          }
        ]
        ```
        Return ONLY a JSON array of such relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.Location_BATTLE_AT: """
        You are a literary relationship analyzer focused on conflict scenes.
        Your task is to extract all BATTLE_AT relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character involved in the battle.
          - "location_id": The _key of the battle location.
          - "chapter": The chapter where the battle is described.
          - "battle_outcome": The outcome of the battle (win, lose, draw).
          - "side": The side or faction the character represented.

        Example:
        ```json
        [
          {
            "character_id": "Char_450",
            "location_id": "Loc_667",
            "chapter": "Chapter 17",
            "battle_outcome": "won",
            "side": "Northern Alliance",
            "casualties": 1200
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Location_LIVES_IN : """
        You are a literary relationship analyzer focusing on residential patterns.
        Your task is to extract all LIVES_IN relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character.
          - "location_id": The _key of the location where the character lives.
          - "start_chapter": The chapter when the character started living at the location.
          - "end_chapter": The chapter when the character left the location (if applicable).
          - "status": The type of residence (permanent, temporary, etc.).

        Example:
        ```json
        [
          {
            "character_id": "Char_123",
            "location_id": "Loc_456",
            "start_chapter": "Chapter 5",
            "end_chapter": "Chap_10
            "status": "permanent"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Emotional_TRUSTS:  """
        You are a literary relationship analyzer specializing in evaluating trust.
        Your task is to extract all TRUSTS relationships among characters from the book.
        For each relationship, return an object with the following keys:
          - "trustor_id": The _key of the character who trusts.
          - "trusted_id": The _key of the character who is trusted.
          - "level": An integer (1-10) indicating the strength of the trust.
          - "chapters": A list of chapters where this trust is evident.
          - "source": A narrative reference if available.

        Example:
        ```json
        [
          {
            "trustor_id": "Char_301",
            "trusted_id": "Char_415",
            "level": 8,
            "chapters": ["Chapter 5", "Chapter 8"],
            "source": "Saved from ambush in Chapter 3"
          }
        ]
        ```
        Return ONLY a JSON array of such relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.Emotional_BETRAYED: """
        You are a literary relationship analyzer focused on conflict and betrayal.
        Your task is to extract all BETRAYED relationships from the book.
        For each relationship, return an object with the following keys:
          - "betrayer_id": The _key of the character who betrayed.
          - "betrayed_id": The _key of the character who was betrayed.
          - "severity": A description or measure of the betrayal’s severity.
          - "motive": The motive behind the betrayal.
          - "chapter": The chapter where the betrayal is described.
        Example:
        ```json
        [
          {
            "betrayer_id": "Char_422",
            "betrayed_id": "Char_199",
            "severity": "High",
            "motive": "Political ambition",
            "chapter": "Chapter 21"
          }
        ]
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.Interaction_INTERACTED_WITH:  """
        You are a literary relationship analyzer focusing on character interactions.
        Your task is to extract all INTERACTED_WITH relationships from the book.
        For each relationship, return an object with the following keys:
          - "character1_id": The _key of one character.
          - "character2_id": The _key of the other character.
          - "interaction_type": The type of interaction (conversation, fight, cooperation, etc.).
          - "chapter": The chapter where the interaction is described.
          - "timestamp": A timestamp if provided.

        Example:
        ```json
        [
          {
            "character1_id": "Char_101",
            "character2_id": "Char_205",
            "interaction_type": "Sword duel",
            "chapter": "Chapter 7",
            "timestamp": "Moonrise of Equinox"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.Interaction_APPEARED_TOGETHER:  """
        You are a literary relationship analyzer focused on character co-occurrences.
        Your task is to extract all APPEARED_TOGETHER relationships from the book.
        For each relationship, return an object with the following keys:
          - "character1_id": The _key of one character.
          - "character2_id": The _key of the other character.
          - "chapter": The chapter where they appear together.
          - "context": A brief description of the context (e.g., feast, council, battle, journey).

        Example:
        ```json
        [
          {
            "character1_id": "Char_045",
            "character2_id": "Char_178",
            "chapter": "Chapter 12",
            "context": "Royal coronation ceremony"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.Interaction_MET_AT:   """
        You are a literary relationship analyzer focused on recording meetings between characters.
        Your task is to extract all MET_AT relationships from the book.
        For each relationship, return an object with the following keys:
          - "character1_id": The _key of one character.
          - "character2_id": The _key of the other character.
          - "chapter": The chapter where the meeting occurred.
          - "location": The location where the meeting took place.
          - "timestamp": A timestamp if provided.

        Example:
        ```json
        [
          {
            "character1_id": "Char_301",
            "character2_id": "Char_422",
            "chapter": "Chapter 3",
            "location": "Abandoned watchtower",
            "timestamp": "Dawn"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.Item_POSSESSES: """
        You are a literary relationship analyzer specializing in character-item interactions.
        Your task is to identify all POSSESSES relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character who possesses the item
          - "item_id": The _key of the item possessed
          - "acquisition_chapter": The chapter in which the item was acquired
          - "current": A boolean indicating if the character currently possesses the item
          - "method": How the item was acquired (found, gifted, stolen, created, inherited)

        Example:
        ```json
        [
          {
            "character_id": "Char_15",
            "item_id": "Item_04",
            "acquisition_chapter": "Chapter 3",
            "current": true,
            "method": "inherited"
          }
        ]
        ```

        Return ONLY a JSON array of such relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.Item_CREATED:  """
        You are a literary relationship analyzer focusing on item creation.
        Your task is to extract all CREATED relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character who created the item.
          - "item_id": The _key of the created item.
          - "chapter": The chapter where the creation is described.
          - "location": The location where the creation occurred.
          - "purpose": The purpose for which the item was created.
          - "materials": The materials used in creating the item.

        Example:
        ```json
        [
          {
            "character_id": "Char_789",
            "item_id": "Item_445",
            "chapter": "Chapter 5",
            "location": "Forge of Durin",
            "purpose": "Dragon slaying",
            "materials": ["mithril", "dragonbone"]
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.Item_SEEKS:  """
        You are a literary relationship analyzer focusing on quest narratives.
        Your task is to extract all SEEKS relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character who is seeking an item.
          - "item_id": The _key of the item being sought.
          - "motivation": The motivation behind the quest for the item.
          - "start_chapter": The chapter when the search begins.
          - "end_chapter": The chapter when the search ends (if applicable).
          - "success": A boolean indicating if the search was successful.

        Example:
        ```json
        [
          {
            "character_id": "Char_178",
            "item_id": "Item_045",
            "motivation": "To cure sister's curse",
            "start_chapter": "Chapter 5",
            "end_chapter": "Chapter 17",
            "success": true
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.Item_DESTROYED:  """
        You are a literary relationship analyzer focusing on destructive events.
        Your task is to extract all DESTROYED relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character who destroyed the item.
          - "item_id": The _key of the item that was destroyed.
          - "chapter": The chapter where the destruction is described.
          - "location": The location where the destruction occurred.
          - "method": The method by which the item was destroyed.
          - "motivation": The motivation behind the destruction.

        Example:
        ```json
        [
          {
            "character_id": "Char_205",
            "item_id": "Item_112",
            "chapter": "Chapter 19",
            "location": "Mount Doom",
            "method": "Volcanic destruction",
            "motivation": "Prevent dark magic resurgence"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.ItemItem_COMPONENT_OF:  """
        You are a literary relationship analyzer focusing on item composition.
        Your task is to extract all COMPONENT_OF relationships from the book.
        For each relationship, return an object with the following keys:
          - "component_item_id": The _key of the item that is a component.
          - "composite_item_id": The _key of the item that the component is part of.
          - "nature": Describe the relationship (e.g., "physical part", "magical link", "transformation").

        Example:
        ```json
        [
          {
            "component_item_id": "Item_56",
            "composite_item_id": "Item_89",
            "nature": "power source",
            "integration_chapter": "Chapter 13",
            "required_for_function": true
          }
        ]
        ```
        Return ONLY a JSON array of such relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.ItemItem_COUNTERS:  """
        You are a literary relationship analyzer focusing on the interplay between items.
        Your task is to extract all COUNTERS relationships from the book.
        For each relationship, return an object with the following keys:
          - "item_id": The _key of the item that counters another.
          - "countered_item_id": The _key of the item that is countered.
          - "method": Describe the method of countering.
          - "effectiveness": Indicate how effective the counter is.
          - "source": Provide a narrative reference if applicable.

        Example:
        ```json
        [
          {
            "item_id": "Item_301",
            "countered_item_id": "Item_422",
            "method": "Nullifies magical energy",
            "effectiveness": "Complete neutralization",
            "source": "Ancient grimoire Chapter 7"
          }
        ]
        ```
        Return ONLY a JSON array of such relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.ItemLocation_LOCATED_AT:  """
        You are a literary relationship analyzer focusing on item placements.
        Your task is to extract all LOCATED_AT relationships from the book.
        For each relationship, return an object with the following keys:
          - "item_id": The _key of the item.
          - "location_id": The _key of the location where the item is found.
          - "chapter_range": The chapter or range of chapters where the item is located.
          - "hidden": A boolean indicating if the item is hidden.
          - "guardian": The _key of the character guarding the item, if applicable.

        Example:
        ```json
        [
          {
            "item_id": "Item_045",
            "location_id": "Loc_789",
            "chapter_range": "Chapters 5-12",
            "hidden": true,
            "guardian": "Char_101"
          }
        ]
        ```
        Return ONLY a JSON array of such relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.ItemLocation_ORIGINATED_FROM:  """
        You are a literary relationship analyzer focusing on item provenance.
        Your task is to extract all ORIGINATED_FROM relationships from the book.
        For each relationship, return an object with the following keys:
          - "item_id": The _key of the item.
          - "location_id": The _key of the location where the item originated.
          - "creation_date": The creation date or time period of the item.
          - "creator": A reference or description of the creator of the item.
          - "significance": The narrative significance of the item's origin.

        Example:
        ```json
        [
          {
            "item_id": "Item_112",
            "location_id": "Loc_301",
            "creation_date": "Second Age 145",
            "creator": "Dwarven Master Smith Durin",
            "significance": "First forged mithril weapon"
          }
        ]
        ```
        Return ONLY a JSON array of such relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    # Event Relationships
    RelationshipType.Event_WITNESSED: """
        You are a literary relationship analyzer focusing on character observations of events.
        Your task is to extract all WITNESSED relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character who witnessed the event.
          - "event_id": The _key of the event that was witnessed.
          - "perspective": The character's perspective or reaction to the event.
          - "chapter": The chapter where this witnessing is described.
          - "distance": How directly the character witnessed the event (e.g., "directly involved", "observed from afar").

        Example:
        ```json
        [
          {
            "character_id": "Char_422",
            "event_id": "Event_045",
            "perspective": "Horrified bystander",
            "chapter": "Chapter 8",
            "distance": "Observed from adjacent building"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Event_PARTICIPATED_IN: """
        You are a literary relationship analyzer focusing on character involvement in events.
        Your task is to extract all PARTICIPATED_IN relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character who participated in the event.
          - "event_id": The _key of the event.
          - "role": The character's role in the event (e.g., "leader", "follower", "victim", "hero").
          - "chapter": The chapter where this participation is described.
          - "outcome": How the event affected the character.

        Example:
        ```json
        [
          {
            "character_id": "Char_22",
            "event_id": "Event_05",
            "role": "organizer",
            "chapter": "Chapter 21",
            "outcome": "Gained political influence"
          }
        ]
        ```

        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Event_CAUSED: """
        You are a literary relationship analyzer specializing in cause-and-effect narratives.
        Your task is to extract all CAUSED relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character who caused the event.
          - "event_id": The _key of the event that was caused.
          - "intention": Whether the character intended to cause this event ("intentional", "unintentional", "indirect").
          - "chapter": The chapter where this causation is described.
          - "method": How the character caused the event.
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Event_AFFECTED_BY: """
        You are a literary relationship analyzer focusing on the impact of events on characters.
        Your task is to extract all AFFECTED_BY relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character affected by the event.
          - "event_id": The _key of the event.
          - "impact": A description of how the event affected the character.
          - "chapter": The chapter where this impact is described.
          - "duration": How long the effect lasted ("temporary", "permanent", "ongoing").

        Example:
        ```json
        [
          {
            "character_id": "Char_101",
            "event_id": "Event_112",
            "impact": "Developed chronic nightmares",
            "chapter": "Chapter 14",
            "duration": "Ongoing"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Event_BORN_AT: """
        You are a literary relationship analyzer focusing on character origins.
        Your task is to extract all BORN_AT relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character who was born.
          - "event_id": The _key of the event during which the character was born.
          - "significance": The significance of this birth timing to the character's story.
          - "chapter": The chapter where this birth is described.
          - "circumstances": A brief description of the birth circumstances.

        Example:
        ```json
        [
          {
            "character_id": "Char_205",
            "event_id": "Event_789",
            "significance": "Born during siege of capital",
            "chapter": "Prologue",
            "circumstances": "Delivered in castle crypt during bombardment"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Event_DIED_AT: """
        You are a literary relationship analyzer focusing on character deaths.
        Your task is to extract all DIED_AT relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character who died.
          - "event_id": The _key of the event during which the character died.
          - "cause": The cause of death.
          - "chapter": The chapter where this death is described.
          - "impact": The narrative impact of this death on the story.

        Example:
        ```json
        [
          {
            "character_id": "Char_178",
            "event_id": "Event_045",
            "cause": "Heroic sacrifice holding bridge",
            "chapter": "Chapter 22",
            "impact": "Enabled army retreat and eventual victory"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    # Organization Relationships
    RelationshipType.Organization_MEMBER_OF: """
        You are a literary relationship analyzer focusing on character affiliations.
        Your task is to extract all MEMBER_OF relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character who is a member.
          - "organization_id": The _key of the organization.
          - "role": The character's role or position within the organization.
          - "join_chapter": The chapter when the character joined the organization.
          - "leave_chapter": The chapter when the character left (if applicable).
          - "status": The current membership status ("active", "former", "honorary").

        Example
        ```json
        [
          {
            "character_id": "Char_330",
            "organization_id": "Org_12",
            "role": "Master of Whispers",
            "join_chapter": "Chapter 3",
            "status": "active",
            "influence_level": "high"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Organization_LEADER_OF: """
        You are a literary relationship analyzer focusing on leadership structures.
        Your task is to extract all LEADER_OF relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character who is a leader.
          - "organization_id": The _key of the led organization.
          - "title": The character's leadership title.
          - "start_chapter": The chapter when leadership began.
          - "end_chapter": The chapter when leadership ended (if applicable).
          - "leadership_style": A brief description of the character's leadership approach.

        Example:
        ```json
        [
          {
            "character_id": "Char_301",
            "organization_id": "Org_07",
            "title": "High Arbiter",
            "start_chapter": "Chapter 2",
            "leadership_style": "Benevolent dictatorship"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Organization_FOUNDED_BY: """
        You are a literary relationship analyzer focusing on organizational origins.
        Your task is to extract all FOUNDED_BY relationships from the book.
        For each relationship, return an object with the following keys:
          - "organization_id": The _key of the organization.
          - "founder_id": The _key of the character who founded the organization.
          - "co_founders": An array of _keys of any co-founders.
          - "foundation_chapter": The chapter when the founding occurred.
          - "purpose": The stated purpose for creating the organization.

        Example:
        ```json
        [
          {
            "organization_id": "Org_12",
            "founder_id": "Char_101",
            "co_founders": ["Char_178", "Char_205"],
            "foundation_chapter": "Chapter 5",
            "purpose": "Resist imperial expansion"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    # Creature Relationships
    RelationshipType.Creature_BELONGS_TO_SPECIES: """
        You are a literary relationship analyzer focusing on character species.
        Your task is to extract all BELONGS_TO_SPECIES relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character.
          - "creature_id": The _key of the species or creature type.
          - "purity": Whether the character is "pure-blooded", "half-blood", or has another heritage description.
          - "chapter": The chapter where this species information is revealed.
          - "traits": Key species traits exhibited by the character.

        Example:
        ```json
        [
          {
            "character_id": "Char_422",
            "creature_id": "Species_03",
            "purity": "Half-blood",
            "chapter": "Chapter 9",
            "traits": ["Night vision", "Enhanced strength"]
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Creature_CONTROLLED_BY: """
        You are a literary relationship analyzer focusing on creature control.
        Your task is to extract all CONTROLLED_BY relationships from the book.
        For each relationship, return an object with the following keys:
          - "creature_id": The _key of the creature being controlled.
          - "controller_id": The _key of the character controlling the creature.
          - "method": The method of control (e.g., "magic", "telepathy", "training").
          - "chapter": The chapter where this control relationship is described.
          - "strength": The strength or reliability of the control ("complete", "partial", "tenuous").

        Example
        ```json
        [
          {
            "creature_id": "Creat_889",
            "controller_id": "Char_002",
            "method": "ancient incantation",
            "chapter": "Chapter 19",
            "strength": "partial",
            "duration": "3 days"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Creature_ALLIED_WITH: """
        You are a literary relationship analyzer focusing on creature alliances.
        Your task is to extract all ALLIED_WITH relationships from the book.
        For each relationship, return an object with the following keys:
          - "creature_id": The _key of the creature or creature group.
          - "ally_id": The _key of the character or group allied with the creature.
          - "nature": The nature of the alliance ("formal", "informal", "temporary").
          - "chapter": The chapter where this alliance is formed or described.
          - "motivation": The motivation behind the alliance for both parties.

        Example:
        ```json
        [
          {
            "creature_id": "Species_07",
            "ally_id": "Org_12",
            "nature": "Temporary",
            "chapter": "Chapter 14",
            "motivation": "Common enemy: Imperial forces"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    # Conceptual Relationships
    RelationshipType.Concept_HAS_ABILITY: """
        You are a literary relationship analyzer focusing on character abilities.
        Your task is to extract all HAS_ABILITY relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character who has the ability.
          - "concept_id": The _key of the concept or ability.
          - "proficiency": The character's level of proficiency with this ability.
          - "chapter": The chapter where this ability is first demonstrated.
          - "source": How the character obtained this ability.
          - "limitations": Any limitations or costs associated with using this ability.

        Example
        ```json
        [
          {
            "character_id": "Char_178",
            "concept_id": "Abil_07",
            "proficiency": "expert",
            "chapter": "Chapter 11",
            "source": "ancient training",
            "limitations": "requires moonlight"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Concept_BELIEVES_IN: """
        You are a literary relationship analyzer focusing on character beliefs.
        Your task is to extract all BELIEVES_IN relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character who holds the belief.
          - "concept_id": The _key of the concept believed in.
          - "strength": The strength of the character's belief ("devout", "moderate", "questioning").
          - "chapter": The chapter where this belief is demonstrated.
          - "manifestation": How this belief manifests in the character's actions.

        Example:
        ```json
        [
          {
            "character_id": "Char_101",
            "concept_id": "Faith_01",
            "strength": "Devout",
            "chapter": "Chapter 3",
            "manifestation": "Wears religious symbols, prays daily"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Concept_RESISTS: """
        You are a literary relationship analyzer focusing on character resistance.
        Your task is to extract all RESISTS relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character who resists.
          - "concept_id": The _key of the concept being resisted.
          - "success": How successful the resistance is ("complete", "partial", "failing").
          - "chapter": The chapter where this resistance is demonstrated.
          - "method": The methods used by the character to resist.
          - "cost": Any costs or consequences of this resistance.

        Example:
        ```json
        [
          {
            "character_id": "Char_205",
            "concept_id": "Corruption_02",
            "success": "Partial",
            "chapter": "Chapter 18",
            "method": "Magical wards",
            "cost": "Chronic fatigue"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Concept_INFLUENCED_BY: """
        You are a literary relationship analyzer focusing on character influences.
        Your task is to extract all INFLUENCED_BY relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character being influenced.
          - "concept_id": The _key of the influencing concept.
          - "nature": The nature of the influence ("corrupting", "inspiring", "confusing").
          - "chapter": The chapter where this influence begins or is most pronounced.
          - "awareness": Whether the character is aware of being influenced.
          - "resistance": The degree to which the character resists the influence.

        Example:
        ```json
        [
          {
            "character_id": "Char_178",
            "concept_id": "Power_05",
            "nature": "Corrupting",
            "chapter": "Chapter 7",
            "awareness": false,
            "resistance": "Low"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    # Temporal Relationships
    RelationshipType.Event_BEFORE: """
        You are a literary relationship analyzer focusing on event chronology.
        Your task is to extract all BEFORE relationships from the book.
        For each relationship, return an object with the following keys:
          - "earlier_event_id": The _key of the event that occurred earlier.
          - "later_event_id": The _key of the event that occurred later.
          - "time_gap": The approximate time between the events.
          - "causality": Whether the earlier event directly caused the later one ("direct", "indirect", "unrelated").
          - "narrative_order": Whether these events are described in chronological order in the book.

        Example:
        ```json
        [
          {
            "earlier_event_id": "Event_22",
            "later_event_id": "Event_45",
            "time_gap": "10 years",
            "causality": "direct",
            "narrative_connection": "foundation for rebellion"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Event_AFTER: """
        You are a literary relationship analyzer focusing on event sequences.
        Your task is to extract all AFTER relationships from the book.
        For each relationship, return an object with the following keys:
          - "later_event_id": The _key of the event that occurred later.
          - "earlier_event_id": The _key of the event that occurred earlier.
          - "time_gap": The approximate time between the events.
          - "consequence": Whether the later event is a consequence of the earlier one.
          - "chapters": The chapters where these events are described.

        Example:
        ```json
        [
          {
            "later_event_id": "Event_112",
            "earlier_event_id": "Event_045",
            "time_gap": "2 years",
            "consequence": true,
            "chapters": ["Chapter 5", "Chapter 7"]
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Event_SIMULTANEOUS_WITH: """
        You are a literary relationship analyzer focusing on concurrent events.
        Your task is to extract all SIMULTANEOUS_WITH relationships from the book.
        For each relationship, return an object with the following keys:
          - "event1_id": The _key of one event.
          - "event2_id": The _key of the other simultaneous event.
          - "exact": Whether the events occur at exactly the same time or just overlap.
          - "significance": The narrative significance of this simultaneity.
          - "awareness": Whether the characters in each event are aware of the other event.
        Example:
        ```json
        [
          {
            "event1_id": "Event_301",
            "event2_id": "Event_422",
            "exact": false,
            "significance": "Demonstrated faction coordination",
            "awareness": "Only leadership knew"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Event_OVERLAPS_WITH: """
        You are a literary relationship analyzer focusing on overlapping events.
        Your task is to extract all OVERLAPS_WITH relationships from the book.
        For each relationship, return an object with the following keys:
          - "event1_id": The _key of one event.
          - "event2_id": The _key of the other overlapping event.
          - "extent": The extent of the overlap ("beginning", "middle", "end", "complete").
          - "interaction": Whether the events directly interact with or influence each other.
          - "perspective": How the overlapping nature is revealed in the narrative.

        Example:
        ```json
        [
          {
            "event1_id": "Event_101",
            "event2_id": "Event_178",
            "extent": "Middle",
            "interaction": "Caused supply line disruptions",
            "perspective": "Revealed through scout reports"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,

    RelationshipType.Event_CAUSES: """
        You are a literary relationship analyzer focusing on causal relationships.
        Your task is to extract all CAUSES relationships from the book.
        For each relationship, return an object with the following keys:
          - "cause_event_id": The _key of the causal event.
          - "effect_event_id": The _key of the resulting event.
          - "directness": How directly the first event caused the second ("direct", "indirect", "catalyst").
          - "inevitability": Whether the effect was inevitable given the cause.
          - "time_gap": The approximate time between cause and effect.

        Examples:
        ```json
        [
          {
            "character_id": "Char_901",
            "event_id": "Event_112",
            "intention": "indirect",
            "chapter": "Chapter 7",
            "method": "poisoned water supply",
            "casualties": 450
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.Event_CAUSED_BY: """
        You are a literary relationship analyzer focusing on event origins.
        Your task is to extract all CAUSED_BY relationships from the book.
        For each relationship, return an object with the following keys:
          - "effect_event_id": The _key of the resulting event.
          - "cause_event_id": The _key of the causal event.
          - "predictability": Whether the effect was predictable from the cause.
          - "intention": Whether the cause intentionally led to this effect.
          - "recognition": Whether characters in the narrative recognize this causal relationship.
        Example:
        ```json
        [
          {
            "effect_event_id": "Event_205",
            "cause_event_id": "Event_301",
            "predictability": "High",
            "intention": true,
            "recognition": "Publicly acknowledged"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """,
    RelationshipType.Item_USED_IN: """
        You are a literary relationship analyzer focusing on item usage in events.
        Your task is to extract all USED_IN relationships from the book.
        For each relationship, return an object with the following keys:
          - "character_id": The _key of the character using the item.
          - "item_id": The _key of the item being used.
          - "event_id": The _key of the event during which the item was used (if applicable).
          - "chapter": The chapter where this usage is described.
          - "purpose": The purpose for which the item was used.
          - "effectiveness": How effective the item was for its intended purpose.
          - "significance": The narrative significance of this usage.
        Example:
        ```json
        [
          {
            "character_id": "Char_422",
            "item_id": "Item_789",
            "event_id": "Event_045",
            "chapter": "Chapter 19",
            "purpose": "Seal dimensional rift",
            "effectiveness": "Partial success",
            "significance": "Prevented total reality collapse"
          }
        ]
        ```
        Return ONLY a JSON array of these relationship objects.
        IMPORTANT: Do not include any markdown formatting or extra text.
        """
    }
