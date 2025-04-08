from enum import Enum

# Entity Types representing significant elements in a book or narrative.
class EntityType(Enum):
    # Individuals or characters, including main protagonists, antagonists, and side characters.
    # Examples: Harry Potter, Sherlock Holmes, Frodo Baggins
    CHARACTER = "Character"

    # Specific places or settings within the narrative, ranging from physical locations to fictional landmarks.
    # Examples: Hogwarts School, Rivendell, King's Landing
    LOCATION = "Location"

    # Individual chapters from the book, excluding prologues or epilogues.
    # Examples: Chapter 1 - "The Boy Who Lived", Chapter 5 - "The Council of Elrond"
    CHAPTER = "Chapter"

    # Important events or occurrences that drive the narrative or significantly impact characters.
    # Examples: The Battle of Hogwarts, Bilbo's Birthday Party, The Fall of the Berlin Wall
    EVENT = "Event"

    # Objects of importance in the story, often central to the plot or character development.
    # Examples: The One Ring, Excalibur Sword, The Elder Wand
    ITEM = "Item"

    # Formal groups, societies, factions, or institutions within the narrative.
    # Examples: The Jedi Order, Gryffindor House, The Avengers
    ORGANIZATION = "Organization"

    # Abstract ideas, beliefs, powers, or magical forces central to the story's theme or plot.
    # Examples: Magic, The Force, Good vs Evil, Time Travel
    CONCEPT = "Concept"

    # Specific species or races prominently featured, especially in fantasy and sci-fi genres.
    # Examples: Elves, Dragons, Orcs, Droids
    CREATURE = "Creature"

    # Clearly defined historical periods or significant points in time mentioned in the narrative.
    # Examples: The Age of Heroes, The Third Age, Summer of 1985
    TIME_PERIOD = "TimePeriod"


# Enum for different types of relationships between entities within the narrative.
class RelationshipType(Enum):

    # Family Relationships (Character ↔ Character)
    Family_PARENT_OF = "PARENT_OF"          # Example: Darth Vader is PARENT_OF Luke Skywalker
    Family_SIBLING_OF = "SIBLING_OF"          # Example: Arya Stark SIBLING_OF Sansa Stark
    Family_MARRIED_TO = "MARRIED_TO"          # Example: Aragorn MARRIED_TO Arwen

    # Emotional Relationships (Character - Character)
    Emotional_LOVES = "LOVES"                 # Example: Romeo LOVES Juliet
    Emotional_TRUSTS = "TRUSTS"               # Example: Harry Potter TRUSTS Albus Dumbledore
    Emotional_BETRAYED = "BETRAYED"           # Example: Brutus BETRAYED Julius Caesar

    # Interaction Relationships (Character ↔ Character)
    Interaction_INTERACTED_WITH = "INTERACTED_WITH"    # Example: Sherlock Holmes INTERACTED_WITH Dr. Watson
    Interaction_APPEARED_TOGETHER = "APPEARED_TOGETHER"# Example: Frodo APPEARED_TOGETHER Samwise
    Interaction_MET_AT = "MET_AT"                      # Example: Gandalf MET_AT Bilbo's Birthday Party

    # Location Relationships (Character - Location)
    Location_PRESENT_AT = "PRESENT_AT"        # Example: Jon Snow PRESENT_AT The Wall
    Location_TRAVELED_TO = "TRAVELED_TO"      # Example: Bilbo TRAVELED_TO Lonely Mountain

    Location_BATTLE_AT = "BATTLE_AT"          # Example: Battle of Helm's Deep BATTLE_AT Helm's Deep
    Location_LIVES_IN = "LIVES_IN"            # Example: Harry Potter LIVES_IN Hogwarts

    # Event Relationships (Character ↔ Event)
    Event_WITNESSED = "WITNESSED"             # Example: Gandalf WITNESSED Fall of Barad-dûr
    Event_PARTICIPATED_IN = "PARTICIPATED_IN" # Example: Jon Snow PARTICIPATED_IN Battle of the Bastards
    Event_CAUSED = "CAUSED"                   # Example: Thanos CAUSED The Snap
    Event_AFFECTED_BY = "AFFECTED_BY"         # Example: Frodo AFFECTED_BY The Destruction of the Ring
    Event_BORN_AT = "BORN_AT"                 # Example: Harry Potter BORN_AT First Wizarding War
    Event_DIED_AT = "DIED_AT"                 # Example: Boromir DIED_AT Battle of Amon Hen

    # Organization Relationships (Character ↔ Organization)
    Organization_MEMBER_OF = "MEMBER_OF"      # Example: Hermione MEMBER_OF Gryffindor House
    Organization_LEADER_OF = "LEADER_OF"      # Example: Gandalf LEADER_OF Fellowship of the Ring
    Organization_FOUNDED_BY = "FOUNDED_BY"    # Example: Hogwarts FOUNDED_BY Four Founders

    # Creature Relationships (Character - Creature)
    Creature_BELONGS_TO_SPECIES = "BELONGS_TO_SPECIES"  # Example: Legolas BELONGS_TO_SPECIES Elves
    Creature_CONTROLLED_BY = "CONTROLLED_BY"            # Example: Drogon CONTROLLED_BY Daenerys
    Creature_ALLIED_WITH = "ALLIED_WITH"                # Example: Ents ALLIED_WITH Hobbits

    # Conceptual Relationships (Character - Concept)
    Concept_HAS_ABILITY = "HAS_ABILITY"       # Example: Yoda HAS_ABILITY The Force
    Concept_BELIEVES_IN = "BELIEVES_IN"       # Example: Obi-Wan BELIEVES_IN Jedi Philosophy
    Concept_RESISTS = "RESISTS"               # Example: Luke RESISTS The Dark Side
    Concept_INFLUENCED_BY = "INFLUENCED_BY"   # Example: Anakin INFLUENCED_BY Emperor Palpatine

    # Temporal Relationships (Event/Event or Event/TimePeriod)
    Event_BEFORE = "BEFORE"                   # Example: Battle of Five Armies BEFORE Destruction of the Ring
    Event_AFTER = "AFTER"                     # Example: Coronation of Aragorn AFTER Battle of Pelennor Fields
    Event_SIMULTANEOUS_WITH = "SIMULTANEOUS_WITH" # Example: Battle of Minas Tirith SIMULTANEOUS_WITH Frodo's journey to Mount Doom
    Event_OVERLAPS_WITH = "OVERLAPS_WITH"     # Example: Siege of Winterfell OVERLAPS_WITH Battle at King's Landing
    Event_CAUSES = "CAUSES"                   # Example: Assassination of Archduke Franz Ferdinand CAUSES World War I
    Event_CAUSED_BY = "CAUSED_BY"             # Example: World War I CAUSED_BY Assassination of Archduke Franz Ferdinand

    # Item Relationships (Character - Item)
    Item_POSSESSES = "POSSESSES"              # Example: Frodo POSSESSES One Ring
    Item_CREATED = "CREATED"                  # Example: Celebrimbor CREATED Rings of Power
    Item_SEEKS = "SEEKS"                      # Example: Voldemort SEEKS Elder Wand
    Item_DESTROYED = "DESTROYED"              # Example: Frodo DESTROYED The One Ring
    Item_USED_IN = "USED_IN"                  # Example: Harry Potter USED_IN Cloak of Invisibility

    # Item-Item Relationships
    ItemItem_COMPONENT_OF = "COMPONENT_OF"    # Example: Sword Hilt COMPONENT_OF Sword
    ItemItem_COUNTERS = "COUNTERS"            # Example: Valyrian Steel COUNTERS White Walkers

    # Item - Location Relationships
    ItemLocation_LOCATED_AT = "LOCATED_AT"          # Example: Excalibur LOCATED_AT Lake
    ItemLocation_ORIGINATED_FROM = "ORIGINATED_FROM"# Example: The One Ring ORIGINATED_FROM Mount Doom