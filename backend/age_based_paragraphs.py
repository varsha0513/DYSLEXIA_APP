"""
Age-Based Reading Assessment Paragraphs
This module contains reading assessment texts selected based on student age
Age is the primary factor for determining appropriate reading difficulty level
"""

# Age-based paragraph library
AGE_BASED_PARAGRAPHS = {
    "4-6": [
        "The cat sat on the mat. It was a warm sunny day. The cat liked naps.",
        "A big red ball rolled down the hill. A boy ran after it fast.",
        "Mom made cookies. They smell yummy. The cookies are warm and soft.",
        "The dog likes to play. It runs and jumps. It has fun all day long.",
        "The sun is bright. It makes things warm. The plants grow big tall."
    ],
    "7-9": [
        "The butterfly flew through the garden. It looked "
        "for nectar. The colors on its wings were beautiful.",
        "Sarah found a seashell on the beach. It was pink "
        "and white. She put it in her treasure box.",
        "The rabbit hopped through the meadow. It looked "
        "for clover to eat. The grass was tall and green.",
        "Tom read a book about dinosaurs. He learned they "
        "were large. Some could run very fast.",
        "The school library has many books. There are "
        "books about animals, space, and adventures."
    ],
    "10-12": [
        ("Photosynthesis is the process by which plants "
         "convert sunlight into chemical energy. The leaves "
         "contain chlorophyll, which absorbs light and "
         "enables the plant to grow. This releases oxygen."),
        ("The water cycle describes how water moves between "
         "earth and atmosphere. Water evaporates from oceans "
         "and lakes, forming clouds. It returns as "
         "precipitation. This cycle is essential for life."),
        ("Ancient civilizations developed writing systems "
         "to record information. Cuneiform was an early "
         "system developed in Mesopotamia. It used "
         "wedge-shaped marks on clay tablets."),
        ("The digestive system breaks down food into "
         "nutrients the body can absorb. The process begins "
         "in the mouth where saliva breaks down food. It "
         "continues through stomach and intestines."),
        ("Magnetic fields are invisible forces created by "
         "moving electric charges. Earth has a magnetic "
         "field protecting us from solar radiation. Magnets "
         "have two poles: north and south.")
    ],
    "13-15": [
        ("The Renaissance was a period of European history "
         "from the 14th to 17th century. It marked the "
         "transition from medieval to modern times. It was "
         "characterized by renewed interest in classical "
         "learning. Artists and scientists made "
         "groundbreaking contributions."),
        ("Evolution is the change in heritable characteristics "
         "of populations over generations. Charles Darwin's "
         "theory of natural selection explains how organisms "
         "adapt to environments. Genetic variation and "
         "environmental pressures drive evolutionary change."),
        ("The Industrial Revolution transformed society "
         "through mechanization and factory systems. It began "
         "in Britain in the late 18th century and spread "
         "globally. This period saw changes in agriculture, "
         "manufacturing, and transportation."),
        ("Ecosystems are communities of organisms interacting "
         "with their environment. Energy flows through food "
         "chains and food webs. Nutrients cycle through "
         "biotic and abiotic components of the ecosystem."),
        ("The Bill of Rights is the first ten amendments to "
         "the United States Constitution. It protects "
         "fundamental freedoms including speech, religion, "
         "and assembly. These amendments were adopted in 1791 "
         "to protect individual liberties.")
    ],
    "16-18": [
        ("Quantum mechanics describes behavior of matter and "
         "energy at atomic scales. It challenges classical "
         "physics and introduces wave-particle duality and "
         "uncertainty principle. Max Planck and Albert "
         "Einstein made foundational contributions."),
        ("Socioeconomic factors significantly influence "
         "educational outcomes and earning potential. "
         "Environmental factors including access to "
         "resources, parental involvement, and school "
         "quality impact achievement. Policy interventions "
         "targeting inequalities show promising results."),
        ("Climate change is driven by anthropogenic greenhouse "
         "gas emissions, particularly carbon dioxide from "
         "fossil fuel combustion. The greenhouse effect "
         "traps heat, causing temperature increases. This "
         "has cascading effects on weather, sea levels, and "
         "biodiversity."),
        ("The Treaty of Versailles ended World War I but "
         "contained terms contributing to future conflict. "
         "Harsh reparations on Germany created resentment "
         "and instability. This period shaped international "
         "relations throughout the 20th century."),
        ("Artificial intelligence and machine learning "
         "revolutionize industries from healthcare to "
         "transportation. Neural networks mimic biological "
         "processes to recognize patterns. Ethical "
         "considerations regarding privacy and algorithmic "
         "bias are increasingly important.")
    ],
    "adult": [
        ("Blockchain technology represents a paradigm shift in "
         "distributed systems and cryptographic security. Its "
         "decentralized architecture eliminates single points "
         "of failure. Applications extend beyond cryptocurrency "
         "to supply chain and smart contracts."),
        ("Neuroplasticity demonstrates that brain structure "
         "and function can be modified throughout life. This "
         "challenges the belief that neural pathways are "
         "fixed. Learning and environmental factors can "
         "strengthen connections and create new pathways."),
        ("The metabolic process converts nutrients into energy "
         "through complex biochemical reactions. Mitochondria "
         "serve as cellular power plants. Understanding "
         "metabolism addresses disorders and optimizes "
         "physical performance."),
        ("Cognitive behavioral therapy is an evidence-based "
         "psychotherapy addressing the relationship between "
         "thoughts, emotions, and behaviors. It helps "
         "individuals identify and challenge maladaptive "
         "patterns. CBT effectively treats depression, "
         "anxiety, and mental health conditions."),
        ("Macroeconomic policy instruments including monetary "
         "and fiscal policy influence aggregate demand and "
         "growth. Central banks adjust interest rates and "
         "money supply. Government spending and taxation "
         "decisions have multiplier effects throughout the "
         "economy.")
    ]}


def get_age_group(age: int) -> str:
    """
    Determine age group based on age value.
    Age is the MOST IMPORTANT factor for paragraph selection.

    Args:
        age (int): User's age in years

    Returns:
        str: Age group key (e.g., "4-6", "7-9", etc.)
    """
    if age is None:
        return "7-9"  # Default to middle group if age not provided

    if age < 7:
        return "4-6"
    elif age < 10:
        return "7-9"
    elif age < 13:
        return "10-12"
    elif age < 16:
        return "13-15"
    elif age < 19:
        return "16-18"
    else:
        return "adult"


def get_paragraph_for_age(age: int, index: int = 0) -> str:
    """
    Get a reading assessment paragraph based on user's age.

    Args:
        age (int): User's age in years
        index (int): Paragraph index (0-4), cycles if out of range

    Returns:
        str: Reading assessment paragraph appropriate for user's age
    """
    age_group = get_age_group(age)
    paragraphs = AGE_BASED_PARAGRAPHS.get(
        age_group, AGE_BASED_PARAGRAPHS["7-9"]
    )

    # Cycle through paragraphs if index is out of range
    safe_index = index % len(paragraphs)

    return paragraphs[safe_index]


def get_all_paragraphs_for_age(age: int) -> list:
    """
    Get all available paragraphs for a given age.

    Args:
        age (int): User's age in years

    Returns:
        list: All paragraphs available for the age group
    """
    age_group = get_age_group(age)
    return AGE_BASED_PARAGRAPHS.get(age_group, AGE_BASED_PARAGRAPHS["7-9"])


def get_age_group_info(age: int) -> dict:
    """
    Get age group info: difficulty level and description.

    Args:
        age (int): User's age in years

    Returns:
        dict: Information about the age group and reading level
    """
    age_group = get_age_group(age)

    descriptions = {
        "4-6": {
            "age_group": "4-6 years",
            "level": "Beginner",
            "difficulty": "Very Easy",
            "focus": "Letter recognition and simple sentences",
            "typical_word_count": "15-20 words per paragraph"
        },
        "7-9": {
            "age_group": "7-9 years",
            "level": "Early Reader",
            "difficulty": "Easy",
            "focus": "Basic sentence construction and comprehension",
            "typical_word_count": "25-40 words per paragraph"
        },
        "10-12": {
            "age_group": "10-12 years",
            "level": "Intermediate",
            "difficulty": "Medium",
            "focus": "Paragraph comprehension and vocabulary building",
            "typical_word_count": "60-100 words per paragraph"
        },
        "13-15": {
            "age_group": "13-15 years",
            "level": "Advanced",
            "difficulty": "Challenging",
            "focus": "Complex ideas and critical thinking",
            "typical_word_count": "120-180 words per paragraph"
        },
        "16-18": {
            "age_group": "16-18 years",
            "level": "High School",
            "difficulty": "Advanced",
            "focus": "Academic content and abstract concepts",
            "typical_word_count": "150-250 words per paragraph"
        },
        "adult": {
            "age_group": "18+ years",
            "level": "Adult",
            "difficulty": "Advanced/Expert",
            "focus": "Complex professional and academic texts",
            "typical_word_count": "200+ words per paragraph"
        }
    }

    return descriptions.get(age_group, descriptions["7-9"])
