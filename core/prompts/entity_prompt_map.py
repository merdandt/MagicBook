from model.entity_types import EntityType


ENTITY_PROMPTS_MAP = {
    EntityType.CHARACTER: """
        You are a literary character analyzer. Your task is to read the provided book text and extract every character mentioned—from major protagonists to minor supporting roles—and identify their properties. Return ONLY a valid JSON array of character objects with the following keys:

        - name: The character's full name (required)
        - gender: The character's gender
        - age: The character's age or age range
        - alive: A boolean indicating if the character is alive at the end of the book
        - status: The character's social status (e.g., noble, commoner, etc.)
        - description: A brief description of the character.
        - occupation: The character's job or role
        - significance: One of Main, Supporting, or Minor

        If you cannot determine a property, use null or omit the property.

        IMPORTANT:
        - Return ONLY the JSON array. Do not include any markdown formatting, explanations, or extra text.
        - Ensure that each JSON item is parsable by Python's json.loads() function.
        - Ensure that the entire return object is parsable by json.loads()
    """,

    EntityType.LOCATION: """
        You are a literary setting analyzer. Your task is to read the provided book text and extract all locations mentioned—from major settings to minor locales—and identify their properties. Return ONLY a valid JSON array of location objects with the following keys:

        - name: The location's name (required)
        - type: Type of location (city, castle, forest, etc.)
        - region: Broader region or country
        - description: A brief description of the location. Tree - four sentences.
        - significance: The location's importance to the story

        If you cannot determine a property, use null or omit the property.

        IMPORTANT:
        - Return ONLY the JSON array. Do not include any markdown formatting, explanations, or extra text.
        - Ensure that each JSON item is parsable by Python's json.loads() function.
        - Ensure that the entire return object is parsable by json.loads()
    """,

    EntityType.CHAPTER: """
        You are a literary structure analyzer. Your task is to read the provided book text and extract information about all chapters or major narrative divisions, and identify their properties. Return ONLY a valid JSON array of chapter objects with the following keys:

        - title: Chapter or scene title (required)
        - position: Numerical position in the narrative
        - summary: A comprehansive summary of the chapter or scene

        If you cannot determine a property, use null or omit the property.

        IMPORTANT:
        - Return ONLY the JSON array. Do not include any markdown formatting, explanations, or extra text.
        - Ensure that each JSON item is parsable by Python's json.loads() function.
        - Ensure that the entire return object is parsable by json.loads()
    """,

    EntityType.EVENT: """
        You are a literary plot analyzer. Your task is to read the provided book text and extract all major events from the narrative and identify their properties. Return ONLY a valid JSON array of event objects with the following keys:

        - name: Name of the event (required)
        - type: Type of event (e.g., battle, ceremony, journey)
        - summary: A comprehansive summary of the event

        If you cannot determine a property, use null or omit the property.

        IMPORTANT:
        - Return ONLY the JSON array. Do not include any markdown formatting, explanations, or extra text.
        - Ensure that each JSON item is parsable by Python's json.loads() function.
        - Ensure that the entire return object is parsable by json.loads()
    """,

    EntityType.ITEM: """
        You are a literary artifact and item analyzer. Your task is to read the provided book text and extract every significant item mentioned—from weapons and magical artifacts to tools and jewelry—and identify their properties. Return ONLY a valid JSON array of item objects with the following keys:

        - name: The item's name (required)
        - type: The type of item (weapon, artifact, jewelry, tool, etc.)
        - magical: A boolean indicating if the item has magical properties
        - description: A comprehansive summary of the item
        - origin: The origin or backstory of the item
        - current_status: The current status (e.g., intact, destroyed, lost)

        If you cannot determine a property, use null or omit the property.

        IMPORTANT:
        - Return ONLY the JSON array. Do not include any markdown formatting, explanations, or extra text.
        - Ensure that each JSON item is parsable by Python's json.loads() function.
        - Ensure that the entire return object is parsable by json.loads()
    """,

    EntityType.ORGANIZATION: """
        You are a literary organization analyzer. Your task is to read the provided book text and extract every organization mentioned—from formal groups, societies, factions, or institutions—and identify their properties. Return ONLY a valid JSON array of organization objects with the following keys:

        - name: The organization's name (required)
        - type: The type of organization (e.g., society, faction, guild, order)
        - description: A brief description of the organization
        - significance: The organization's importance to the narrative

        If you cannot determine a property, use null or omit the property.

        IMPORTANT:
        - Return ONLY the JSON array. Do not include any markdown formatting, explanations, or extra text.
        - Ensure that each JSON item is parsable by Python's json.loads() function.
        - Ensure that the entire return object is parsable by json.loads()
    """,

    EntityType.CONCEPT: """
        You are a literary concept analyzer. Your task is to read the provided book text and extract abstract ideas, beliefs, or magical forces that are central to the narrative’s theme or plot. Return ONLY a valid JSON array of concept objects with the following keys:

        - name: The concept's name or title (required)
        - description: A comprehansive summary of the concept and its role in the narrative

        If you cannot determine a property, use null or omit the property.

        IMPORTANT:
        - Return ONLY the JSON array. Do not include any markdown formatting, explanations, or extra text.
        - Ensure that each JSON item is parsable by Python's json.loads() function.
        - Ensure that the entire return object is parsable by json.loads()
    """,

    EntityType.CREATURE: """
        You are a literary creature analyzer. Your task is to read the provided book text and extract every creature, species, or race mentioned—from mythical beings to scientifically created entities—and identify their properties. Return ONLY a valid JSON array of creature objects with the following keys:

        - name: The creature's name (required)
        - description: A brief description of the creature
        - significance: The creature's role in the narrative

        If you cannot determine a property, use null or omit the property.

        IMPORTANT:
        - Return ONLY the JSON array. Do not include any markdown formatting, explanations, or extra text.
        - Ensure that each JSON item is parsable by Python's json.loads() function.
        - Ensure that the entire return object is parsable by json.loads()
    """,

    EntityType.TIME_PERIOD: """
        You are a literary time period analyzer. Your task is to read the provided book text and extract every clearly defined historical period or significant point in time mentioned in the narrative. Return ONLY a valid JSON array of time period objects with the following keys:

        - name: The name or label of the time period (required)
        - description: A brief description of the time period and its significance in the narrative

        If you cannot determine a property, use null or omit the property.

        IMPORTANT:
        - Return ONLY the JSON array. Do not include any markdown formatting, explanations, or extra text.
        - Ensure that each JSON item is parsable by Python's json.loads() function.
        - Ensure that the entire return object is parsable by json.loads()
    """
}
