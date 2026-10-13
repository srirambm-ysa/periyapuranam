"""Shared yappu card DB + PP metre-label map (single source).

Cards: aruseer / kochakam / ezhucir (Moorkka v11 record) +
aintucir / encir / kaliviruttam (TK track, Gemini call 2026-09-26).
Builders import YAPPU_DB_JS and label_to_key; never hand-edit
cards in templates or per-story builders. build_moorkka_pilot.py
keeps its embedded v11 copy frozen (do not touch).
"""

YAPPU_DB_JS = """const yappuDatabase = {
            "aruseer-viruttham": {
                nameEn: "Aruseer Kazhinediladi Asiriya Viruttham",
                nameTa: "அறுசீர்க் கழிநெடிலடி ஆசிரிய விருத்தம்",
                math: {
                    anatomy: "4 lines, 6 metrical feet per line — 24 feet per stanza",
                    syllables: "Kai-seer feet ending in Naer (நேர்)",
                    rhyme: "2nd-letter ethukai across 4 lines; monai alliteration 1st-4th foot"
                },
                mood: {
                    cadence: "Ahaval Osai — fluid, narrative, deeply devotional",
                    effect: "Majestic epic momentum; Sekkizhar paints vivid drama without slowing narrative speed."
                },
                craft: {
                    difficulty: "High",
                    challenge: "Fitting dense Tamil sandhi into exact 6-foot lines while preserving 2nd-letter rhyme."
                },
                singing: {
                    pann: "Nattapaadai / Thakkakesi",
                    raga: "Nattai / Gambheeranattai or Mayamalavagowla",
                    pause: "Pause after the 3rd foot in each line (3 + 3 = 6)."
                }
            },
            "kochakam-kalippa": {
                nameEn: "Kochchaka Kalippa",
                nameTa: "கொச்சகக் கலிப்பா",
                math: {
                    anatomy: "Mixed Kalippa limbs (taravu opening + thazhisai); Moorkka 8-12 run as 4-line stanzas",
                    syllables: "Kali feet with Thullal Osai rhythm",
                    rhyme: "Ethukai across lines with kalippa-internal limb rhymes"
                },
                mood: {
                    cadence: "Thullal Osai — leaping, dramatic, urgent",
                    effect: "Sekkizhar shifts gear for the gambling drama: pace quickens, moral tension rises, then resolves into grace."
                },
                craft: {
                    difficulty: "Very High",
                    challenge: "Holding mixed taravu/thazhisai limbs together while the story accelerates."
                },
                singing: {
                    pann: "Kolli / Thakkakesi (odhuvan marabu)",
                    raga: "Pantuvarali / Kalyani family",
                    pause: "Break after each limb; chant thazhisai passages briskly."
                }
            },
            "ezhucir-viruttham": {
                nameEn: "Ezhuseer Kazhinediladi Asiriya Viruttham",
                nameTa: "எழுசீர்க் கழிநெடிலடி ஆசிரிய விருத்தம்",
                math: {
                    anatomy: "4 lines, 7 metrical feet per line — 28 feet per stanza",
                    syllables: "Mixed kai-seer feet ending in Naer",
                    rhyme: "2nd-letter ethukai across lines; monai alliteration"
                },
                mood: {
                    cadence: "Ahaval Osai — grave, weighty, processional",
                    effect: "Seven-foot lines carry catalogue and praise passages: Thogai's roll-call of saints, Anthathi's compressed hagiography."
                },
                craft: {
                    difficulty: "High",
                    challenge: "Sustaining the long 7-foot line without slack while keeping second-letter rhyme exact."
                },
                singing: {
                    pann: "Nattapaadai / Thakkakesi",
                    raga: "Nattai / Mayamalavagowla family",
                    pause: "Pause after the 4th foot (4 + 3 = 7)."
                }
            },
            "aintucir-kalithurai": {
                nameEn: "Aintucir Kalithurai",
                nameTa: "ஐந்துசீர் கலித்துறை",
                math: {
                    anatomy: "4 lines, 5 metrical feet per line — 20 feet per stanza",
                    syllables: "Kali feet in Thullal Osai rhythm",
                    rhyme: "2nd-letter ethukai across lines; monai alliteration"
                },
                mood: {
                    cadence: "Thullal Osai — leaping, energetic, urgent",
                    effect: "Carries fast narrative and fervent devotion; Sekkizhar sustains pace through wonder passages without slack."
                },
                craft: {
                    difficulty: "High",
                    challenge: "Holding exact 5-foot lines with rhyme while the story runs at full speed."
                },
                singing: {
                    pann: "Panchamam",
                    raga: "Ahiri family",
                    pause: "Pause after the 2nd foot (2 + 3 = 5)."
                }
            },
            "encir-viruttham": {
                nameEn: "Encir Kazhinediladi Asiriya Viruttham",
                nameTa: "எண்சீர்க் கழிநெடிலடி ஆசிரிய விருத்தம்",
                math: {
                    anatomy: "4 lines, 8 metrical feet per line — 32 feet per stanza",
                    syllables: "Kai-seer feet ending in Naer, strong mid-line caesura",
                    rhyme: "2nd-letter ethukai across 4 lines; monai alliteration"
                },
                mood: {
                    cadence: "Ahaval Osai — majestic, expansive, contemplative",
                    effect: "Grandeur and detailed praise; Sekkizhar slows time for divine acts and saintly virtues."
                },
                craft: {
                    difficulty: "High",
                    challenge: "Filling 8 long feet per line with imagery that never sags, under strict rhyme."
                },
                singing: {
                    pann: "Indalam",
                    raga: "Kedaragowla family",
                    pause: "Pause after the 4th foot (4 + 4 = 8)."
                }
            },
            "kaliviruttam": {
                nameEn: "Kaliviruttam",
                nameTa: "கலிவிருத்தம் (நான்கு சீர்)",
                math: {
                    anatomy: "4 lines, 4 metrical feet per line — 16 feet per stanza",
                    syllables: "Kali feet in Thullal Osai rhythm",
                    rhyme: "2nd-letter ethukai across lines; monai alliteration"
                },
                mood: {
                    cadence: "Thullal Osai — brisk, direct, lively",
                    effect: "Concise turns of event and pointed devotional statement in the shortest Kali gear."
                },
                craft: {
                    difficulty: "Moderate",
                    challenge: "Compression: full meaning and emotion inside 4 short feet per line."
                },
                singing: {
                    pann: "Kurinji",
                    raga: "Harikambhoji family",
                    pause: "Pause after the 2nd foot (2 + 2 = 4)."
                }
            }
        };"""


def label_to_key(label):
    """shaivam Tamil metre label -> card key; None = fallback."""
    t = label or ""
    if "எண்சீர்" in t:
        return "encir-viruttham"
    if "ஐந்துசீர்" in t or "ஐஞ்சீர்" in t:
        return "aintucir-kalithurai"
    if "எழுசீர்" in t:
        return "ezhucir-viruttham"
    if "அறுசீர்" in t:
        return "aruseer-viruttham"
    if "கொச்சக" in t:
        return "kochakam-kalippa"
    if "கலிவிருத்தம்" in t:
        return "kaliviruttam"
    # Kalithurai family (decision 2026-10-13, data-backed, not drive-by):
    # bare கலித்துறை / கலிநிலைத்துறை and சந்தம்-/கட்டளை-qualified variants
    # share the identical 4-adi stanza geometry of the explicit
    # ஐந்துசீர்-கலித்துறை songs in the same sections (Murthi 28 explicit +
    # 19 bare, same poet), so they take the same aintucir-kalithurai card.
    # வஞ்சி விருத்தம் deliberately left unmapped (own pa, needs new card).
    if "கலிநிலைத்துறை" in t:
        return "aintucir-kalithurai"
    if "கலித்துறை" in t:
        return "aintucir-kalithurai"
    return None
