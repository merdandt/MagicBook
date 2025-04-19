from enum import Enum
import inspect

import enum

def enum_to_string(enum_class):
    """Represents an enum class as a string with all values."""
    result = f"Enum: {enum_class.__name__}\n"
    for member in enum_class:
        result += f"- {member.name}: {member.value}\n"
    return result

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

    # Example: Darth Vader is PARENT_OF Luke Skywalker
    Family_PARENT_OF = "PARENT_OF"
    # Example: Arya Stark SIBLING_OF Sansa Stark
    Family_SIBLING_OF = "SIBLING_OF"
    # Example: Aragorn MARRIED_TO Arwen
    Family_MARRIED_TO = "MARRIED_TO"

    # Emotional Relationships (Character - Character)

    # Example: Romeo LOVES Juliet
    Emotional_LOVES = "LOVES"
    # Example: Harry Potter TRUSTS Albus Dumbledore
    Emotional_TRUSTS = "TRUSTS"
    # Example: Brutus BETRAYED Julius Caesar
    Emotional_BETRAYED = "BETRAYED"

    # Interaction Relationships (Character ↔ Character)

    # Example: Sherlock Holmes INTERACTED_WITH Dr. Watson
    Interaction_INTERACTED_WITH = "INTERACTED_WITH"
    # Example: Gandalf APPEARED_TOGETHER with Frodo (Corrected example for clarity)
    Interaction_APPEARED_TOGETHER = "APPEARED_TOGETHER"
    # Example: Gandalf MET_AT Bilbo's Birthday Party
    Interaction_MET_AT = "MET_AT"

    # Location Relationships (Character - Location)

    # Example: Jon Snow PRESENT_AT The Wall
    Location_PRESENT_AT = "PRESENT_AT"
    # Example: Bilbo TRAVELED_TO Lonely Mountain
    Location_TRAVELED_TO = "TRAVELED_TO"
    # Example: Battle of Helm's Deep BATTLE_AT Helm's Deep
    Location_BATTLE_AT = "BATTLE_AT"
    # Example: Harry Potter LIVES_IN Hogwarts
    Location_LIVES_IN = "LIVES_IN"

    # Event Relationships (Character ↔ Event)

    # Example: Gandalf WITNESSED Fall of Barad-dûr
    Event_WITNESSED = "WITNESSED"
    # Example: Jon Snow PARTICIPATED_IN Battle of the Bastards
    Event_PARTICIPATED_IN = "PARTICIPATED_IN"
    # Example: Thanos CAUSED The Snap
    Event_CAUSED = "CAUSED"
    # Example: Frodo AFFECTED_BY The Destruction of the Ring
    Event_AFFECTED_BY = "AFFECTED_BY"
    # Example: Harry Potter BORN_AT First Wizarding War
    Event_BORN_AT = "BORN_AT"
    # Example: Boromir DIED_AT Battle of Amon Hen
    Event_DIED_AT = "DIED_AT"

    # Organization Relationships (Character ↔ Organization)

    # Example: Hermione MEMBER_OF Gryffindor House
    Organization_MEMBER_OF = "MEMBER_OF"
    # Example: Gandalf LEADER_OF Fellowship of the Ring
    Organization_LEADER_OF = "LEADER_OF"
    # Example: Hogwarts FOUNDED_BY Four Founders
    Organization_FOUNDED_BY = "FOUNDED_BY"

    # Creature Relationships (Character - Creature)

    # Example: Legolas BELONGS_TO_SPECIES Elves
    Creature_BELONGS_TO_SPECIES = "BELONGS_TO_SPECIES"
    # Example: Drogon CONTROLLED_BY Daenerys
    Creature_CONTROLLED_BY = "CONTROLLED_BY"
    # Example: Ents ALLIED_WITH Hobbits
    Creature_ALLIED_WITH = "ALLIED_WITH"

    # Conceptual Relationships (Character - Concept)

    # Example: Yoda HAS_ABILITY The Force
    Concept_HAS_ABILITY = "HAS_ABILITY"
    # Example: Obi-Wan BELIEVES_IN Jedi Philosophy
    Concept_BELIEVES_IN = "BELIEVES_IN"
    # Example: Luke RESISTS The Dark Side
    Concept_RESISTS = "RESISTS"
    # Example: Anakin INFLUENCED_BY Emperor Palpatine
    Concept_INFLUENCED_BY = "INFLUENCED_BY"

    # Temporal Relationships (Event/Event or Event/TimePeriod)

    # Example: Battle of Five Armies BEFORE Destruction of the Ring
    Event_BEFORE = "BEFORE"
    # Example: Coronation of Aragorn AFTER Battle of Pelennor Fields
    Event_AFTER = "AFTER"
    # Example: Battle of Minas Tirith SIMULTANEOUS_WITH Frodo's journey to Mount Doom
    Event_SIMULTANEOUS_WITH = "SIMULTANEOUS_WITH"
    # Example: Siege of Winterfell OVERLAPS_WITH Battle at King's Landing
    Event_OVERLAPS_WITH = "OVERLAPS_WITH"
    # Example: Assassination of Archduke Franz Ferdinand CAUSES World War I
    Event_CAUSES = "CAUSES"
    # Example: World War I CAUSED_BY Assassination of Archduke Franz Ferdinand
    Event_CAUSED_BY = "CAUSED_BY"

    # Item Relationships (Character - Item)

    # Example: Frodo POSSESSES One Ring
    Item_POSSESSES = "POSSESSES"
    # Example: Celebrimbor CREATED Rings of Power
    Item_CREATED = "CREATED"
    # Example: Voldemort SEEKS Elder Wand
    Item_SEEKS = "SEEKS"
    # Example: Frodo DESTROYED The One Ring
    Item_DESTROYED = "DESTROYED"
    # Example: Harry Potter USED_IN Cloak of Invisibility
    Item_USED_IN = "USED_IN"

    # Item-Item Relationships

    # Example: Sword Hilt COMPONENT_OF Sword
    ItemItem_COMPONENT_OF = "COMPONENT_OF"
    # Example: Valyrian Steel COUNTERS White Walkers
    ItemItem_COUNTERS = "COUNTERS"

    # Item - Location Relationships

    # Example: Excalibur LOCATED_AT Lake
    ItemLocation_LOCATED_AT = "LOCATED_AT"
    # Example: The One Ring ORIGINATED_FROM Mount Doom
    ItemLocation_ORIGINATED_FROM = "ORIGINATED_FROM"





