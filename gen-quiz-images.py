#!/usr/bin/env python3
"""Generate News Quiz images + quiz-data.json for today
   Categories: Germany, World, History (random events + random art styles)
   + Collage images in Bosch / Van Gogh style
"""

import os, json, base64, urllib.request, datetime, shutil, random, hashlib

OPENAI_API_KEY      = os.environ.get("OPENAI_API_KEY", "")
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
OUT_DIR  = "/var/www/shelldon.monoroc.de/games/ai-news-quiz/images"
JSON_PATH = "/var/www/shelldon.monoroc.de/games/ai-news-quiz/quiz-data.json"
WEBROOT  = "/var/www/shelldon.monoroc.de/games/ai-news-quiz"
MODEL    = "dall-e-3"

# ─────────────────────────────────────────────────────────────
# TODAY'S NEWS  (update daily)
# ─────────────────────────────────────────────────────────────
CATEGORIES = {
    "germany": [
        {
            "id": "de1",
            "headline": "MSC 2026: Kluft zwischen USA und Europa bleibt – Rubio beschwört transatlantische Einheit, Pistorius und Merz kritisch",
            "source": "Tagesschau / DW",
            "prompt": "A dramatic diplomatic scene at the Munich Security Conference: American and European officials face each other across a wide divide symbolized as a physical crack in the conference room floor, US and EU flags on either side, serious faces in suits, grand hotel conference hall, editorial photorealistic illustration"
        },
        {
            "id": "de2",
            "headline": "Inflation trifft Ostdeutschland besonders hart – neue Daten zeigen wachsende regionale Ungleichheit",
            "source": "Der Spiegel",
            "prompt": "A split map of Germany where the eastern half is shown in deep red with rising price tags and worried shoppers at grocery stores, the western half in lighter tones, bar charts showing diverging inflation rates, stark and informative editorial illustration style"
        },
        {
            "id": "de3",
            "headline": "Rodel-Gold! Max Langenhan holt Deutschlands ersten Olympiasieg bei den Winterspielen 2026 in Mailand",
            "source": "DPA / deutschland.de",
            "prompt": "A triumphant German luge athlete in full racing suit standing on the Olympic gold podium in a snow-capped Italian alpine setting, gold medal gleaming, German flag raised, crowd cheering, cinematic sports photography style, warm celebratory light"
        },
        {
            "id": "de4",
            "headline": "Ramadan 2026 beginnt in Deutschland – Millionen Muslime starten am 18. Februar in den Fastenmonat",
            "source": "Morocco World News",
            "prompt": "A twilight scene of a mosque in a German city at dusk, crescent moon and star visible in the sky, families gathering for iftar dinner at long communal tables outside, warm lantern light, celebratory and peaceful atmosphere, editorial illustration"
        }
    ],
    "world": [
        {
            "id": "wo1",
            "headline": "Iran says 'guiding principles' agreed with US at nuclear talks – more work needed for final deal",
            "source": "BBC News",
            "prompt": "Diplomats from Iran and the United States seated across a polished negotiating table in a neutral conference room, American and Iranian flags on stands, documents being exchanged, cautious hopeful expressions, soft diplomatic lighting, photorealistic editorial illustration"
        },
        {
            "id": "wo2",
            "headline": "'We're going to always be grateful' – Chicago mourns civil rights icon Jesse Jackson, dead at 84",
            "source": "BBC News",
            "prompt": "A golden dove ascending over the Chicago skyline at dusk, silhouettes of mourners below holding candles and signs, warm emotional light breaking through clouds, a crowd gathered at a memorial with flowers and photographs, powerful and tender tribute illustration"
        },
        {
            "id": "wo3",
            "headline": "Peru's president José Jerí impeached just four months into term – the country's seventh ousted leader since 2016",
            "source": "BBC News",
            "prompt": "A Peruvian presidential sash lying abandoned on the floor of a grand congress chamber, lawmakers in heated debate around it, Andean motifs on the walls, a revolving door metaphor in the background symbolizing the cycle of ousted leaders, editorial illustration"
        },
        {
            "id": "wo4",
            "headline": "Rescuers race to find 10 missing skiers after massive California avalanche – 30 inches of snow in 24 hours",
            "source": "BBC News",
            "prompt": "Emergency rescue workers in bright orange gear trudging through deep snow in a dramatic Sierra Nevada mountain scene, search dogs, helicopters overhead, towering avalanche debris fields, tense urgent atmosphere, cinematic winter rescue illustration"
        }
    ]
}

# ─────────────────────────────────────────────────────────────
# COLLAGE PROMPTS
# ─────────────────────────────────────────────────────────────
COLLAGE_PROMPTS = {
    "germany": {
        "bosch": {
            "style": "Hieronymus Bosch",
            "prompt": (
                "In the dark fantastical style of Hieronymus Bosch, a single complex painting depicting four German news stories simultaneously: "
                "1) American and European diplomatic demons and angels facing off across a great chasm at a grand conference, flags as banners; "
                "2) Tiny citizens in an eastern German town being crushed by giant floating price tags and coins while western towns glow peacefully; "
                "3) A triumphant Germanic hero in luge armor ascending to a golden throne on an icy mountain, crowds celebrating below; "
                "4) A moonlit mosque with a crescent moon above, families feasting at long tables surrounded by lantern-carrying figures. "
                "Dense, symbolic, medieval hell-garden aesthetic, richly detailed, oil painting style."
            )
        },
        "vangogh": {
            "style": "Vincent van Gogh",
            "prompt": (
                "In the swirling expressive style of Van Gogh, a single vivid painting with four panels blending together: "
                "1) Suited diplomats on either side of a swirling rift, American and European flags like whirling banners; "
                "2) A stormy eastern German town with swirling price-tag vortexes looming over market stalls; "
                "3) A jubilant athlete on an icy mountain podium, gold medal glinting in swirling Alpine light; "
                "4) A glowing crescent moon over a domed mosque, swirling warm lantern light, families gathered below. "
                "Thick impasto brushstrokes, vibrant colors, emotional intensity."
            )
        }
    },
    "world": {
        "bosch": {
            "style": "Hieronymus Bosch",
            "prompt": (
                "In the dark fantastical style of Hieronymus Bosch, a complex painting showing four world news stories: "
                "1) Iranian and American imp-like diplomats exchanging glowing scrolls over a bubbling cauldron of nuclear symbols; "
                "2) A golden dove ascending above a grieving Chicago crowd, the spirit of Jesse Jackson rising in heavenly light; "
                "3) A Peruvian leader tumbling from a gilded throne as a revolving door spins endlessly in the background; "
                "4) Tiny rescue workers in orange armor crawling through a vast white avalanche landscape searching for lost souls. "
                "Rich symbolic detail, dark medieval fantasy, oil painting style."
            )
        },
        "vangogh": {
            "style": "Vincent van Gogh",
            "prompt": (
                "In the swirling expressive style of Van Gogh, a single vivid painting with four blending scenes: "
                "1) Iranian and US diplomats at a table beneath a swirling starry Middle Eastern sky, atomic symbols dissolving into doves; "
                "2) A glowing golden dove soaring over Chicago's swirling skyline at dusk, candlelit mourners below; "
                "3) A Peruvian congress chamber with swirling debate and a fallen presidential sash, Andean mountains in the distance; "
                "4) Orange-clad rescuers in swirling white snow, helicopters overhead, dramatic Sierra Nevada peaks around them. "
                "Thick expressive brushstrokes, bold colors, emotional depth."
            )
        }
    }
}

# ─────────────────────────────────────────────────────────────
# HISTORICAL EVENTS POOL  (200 AD → 2010)
# ─────────────────────────────────────────────────────────────
HISTORICAL_EVENTS = [
    # ── 200–500 AD ──
    {"id": "h_001", "year": 285,
     "headline": "Diocletian Splits the Roman Empire (285 AD)",
     "prompt_base": "Emperor Diocletian in golden armor seated on a throne, splitting a grand map of his empire in two, Roman senators watching, eagles representing east and west, marble columns, imperial grandeur"},
    {"id": "h_002", "year": 313,
     "headline": "Edict of Milan Legalizes Christianity (313 AD)",
     "prompt_base": "Emperor Constantine holding a golden scroll with a cross above him, crowds of Christians joyfully emerging from catacombs into sunlight, ancient Rome skyline, momentous dawn"},
    {"id": "h_003", "year": 410,
     "headline": "Visigoths Sack Rome (410 AD)",
     "prompt_base": "Barbarian warriors on horseback flooding through Rome's ancient gates, citizens fleeing with treasures, fires in the background, the Colosseum visible, dramatic historical chaos"},
    {"id": "h_004", "year": 476,
     "headline": "Fall of the Western Roman Empire (476 AD)",
     "prompt_base": "A young boy emperor handing his crown to a towering Germanic chieftain, Roman legionaries laying down their shields at sunset over crumbling Roman architecture, the end of an era"},
    # ── 500–1000 AD ──
    {"id": "h_005", "year": 793,
     "headline": "Vikings Raid Lindisfarne Monastery (793 AD)",
     "prompt_base": "Norse longships emerging from morning fog onto a rocky northern coastline, fierce Viking warriors storming a peaceful monastery, monks fleeing, rough northern seas and dramatic skies"},
    {"id": "h_006", "year": 800,
     "headline": "Charlemagne Crowned Holy Roman Emperor (800 AD)",
     "prompt_base": "Pope Leo III placing a golden crown on the kneeling Charlemagne in a candlelit cathedral on Christmas night, gathered nobles and bishops watching, Byzantine mosaics glowing"},
    {"id": "h_007", "year": 570,
     "headline": "Birth of Muhammad, Prophet of Islam (570 AD)",
     "prompt_base": "The ancient city of Mecca at night under a brilliant starlit sky, the Kaaba at center, pilgrims in flowing robes, a golden crescent moon, mystical light over the Arabian desert"},
    {"id": "h_008", "year": 962,
     "headline": "Otto I Founds the Holy Roman Empire (962 AD)",
     "prompt_base": "Otto I in full imperial regalia receiving his crown in Rome, German and Italian nobles watching, eagle banner raised high, medieval ceremony at dawn"},
    # ── 1000–1400 AD ──
    {"id": "h_009", "year": 1066,
     "headline": "Norman Conquest: Battle of Hastings (1066 AD)",
     "prompt_base": "Norman knights on horseback clashing with Anglo-Saxon shield wall at Hastings, arrows filling the sky, banners of both sides, mud and chaos of medieval battle, dramatic dusk sky"},
    {"id": "h_010", "year": 1096,
     "headline": "The First Crusade Begins (1096 AD)",
     "prompt_base": "A vast army of crusaders in chainmail with red cross banners marching toward the horizon, castles and cathedrals behind them, Jerusalem shimmering in the distant heat, epic medieval landscape"},
    {"id": "h_011", "year": 1215,
     "headline": "Magna Carta Signed at Runnymede (1215 AD)",
     "prompt_base": "King John seated on a throne in an open field, surrounded by armed barons in armor, reluctantly pressing his seal into a large parchment document, a great river and green meadow behind"},
    {"id": "h_012", "year": 1241,
     "headline": "Mongols Invade Europe (1241 AD)",
     "prompt_base": "A vast Mongol cavalry charging across snow-covered Eastern European plains, burning villages behind them, terrified European knights, the Mongol banner against a stormy dramatic sky"},
    {"id": "h_013", "year": 1347,
     "headline": "The Black Death Reaches Europe (1347 AD)",
     "prompt_base": "Medieval European town in the grip of plague, physicians in beak-shaped masks, survivors praying in the streets, dark clouds and ravens overhead, the chilling atmosphere of catastrophe"},
    {"id": "h_014", "year": 1295,
     "headline": "Marco Polo Returns from China (1295 AD)",
     "prompt_base": "Marco Polo arriving back in Venice by boat after 24 years, laden with exotic silks and spices, Venetian citizens astonished, the Grand Canal and domed basilica behind him"},
    # ── 1400–1600 AD ──
    {"id": "h_015", "year": 1440,
     "headline": "Gutenberg Invents the Printing Press (~1440 AD)",
     "prompt_base": "Johannes Gutenberg in his workshop operating the first printing press, freshly printed pages drying, books stacked around him, scholars astonished, late medieval Germany"},
    {"id": "h_016", "year": 1453,
     "headline": "Fall of Constantinople to the Ottomans (1453 AD)",
     "prompt_base": "Ottoman cannons bombarding the massive ancient walls of Constantinople, Sultan Mehmed II on white horse watching the assault, the Hagia Sophia visible through the smoke and fire"},
    {"id": "h_017", "year": 1492,
     "headline": "Columbus Reaches the Americas (1492 AD)",
     "prompt_base": "Three tall ships arriving at a lush tropical shore, indigenous people watching from the beach in astonishment, explorers planting a flag in the sand, twilight sky over a new world"},
    {"id": "h_018", "year": 1517,
     "headline": "Luther Posts His 95 Theses (1517 AD)",
     "prompt_base": "A monk in robes hammering a parchment document to the grand wooden door of a church, onlookers gathering in amazement, dawn light over a German town, a defiant act that changed history"},
    {"id": "h_019", "year": 1543,
     "headline": "Copernicus Publishes the Heliocentric Model (1543 AD)",
     "prompt_base": "An astronomer in a tower observatory, studying the night sky, his revolutionary diagram showing planets orbiting the Sun spread before him, stars above, quiet revolutionary moment"},
    {"id": "h_020", "year": 1522,
     "headline": "Magellan's Crew Completes First Circumnavigation (1522 AD)",
     "prompt_base": "A battered Spanish sailing ship with ragged sails arriving back in harbor, exhausted but triumphant crew, globes and maps scattered about, the world proved round for the first time"},
    {"id": "h_021", "year": 1588,
     "headline": "The Spanish Armada is Defeated (1588 AD)",
     "prompt_base": "English fireships burning through the great Spanish Armada in stormy seas, galleons in chaos, lightning and fire, English sailors watching triumphantly from their faster ships, dramatic naval battle"},
    # ── 1600–1800 AD ──
    {"id": "h_022", "year": 1620,
     "headline": "Pilgrims Land at Plymouth Rock (1620 AD)",
     "prompt_base": "Weary Pilgrims wading ashore from a longboat in winter, their ship anchored offshore, a barren New England coast in late autumn, the founding of a new colony"},
    {"id": "h_023", "year": 1648,
     "headline": "Peace of Westphalia Ends the Thirty Years War (1648)",
     "prompt_base": "European diplomats in elaborate baroque dress signing peace treaties in a grand hall, relief on exhausted faces after decades of religious war, candles and chandeliers, momentous ceremony"},
    {"id": "h_024", "year": 1687,
     "headline": "Newton Publishes the Laws of Motion (1687)",
     "prompt_base": "A scientist sitting beneath an apple tree in an English garden, an apple falling toward him, mathematical equations swirling around like a vision, books and a telescope nearby, golden afternoon light"},
    {"id": "h_025", "year": 1755,
     "headline": "The Great Lisbon Earthquake (1755 AD)",
     "prompt_base": "Lisbon's grand baroque buildings collapsing in a massive earthquake on All Saints Day, churches crumbling while candles spark fires, survivors fleeing, a great city reduced to ruins"},
    {"id": "h_026", "year": 1776,
     "headline": "American Declaration of Independence (1776)",
     "prompt_base": "Founding Fathers gathered in a grand hall signing a historic document, powdered wigs and colonial dress, sunlight streaming through tall windows, a new nation being born"},
    {"id": "h_027", "year": 1789,
     "headline": "Storming of the Bastille (1789)",
     "prompt_base": "Thousands of Parisian citizens storming a fortress, smoke from muskets, revolutionary tricolor flags, guards on the ramparts, crowds wielding pikes and torches, the dawn of revolution"},
    {"id": "h_028", "year": 1793,
     "headline": "Louis XVI Executed by Guillotine (1793)",
     "prompt_base": "A guillotine in a Paris square, a massive watching crowd in tricolor cockades, revolutionary guards, Notre Dame cathedral in the grey winter background, a king's final moment"},
    # ── 1800–1900 ──
    {"id": "h_029", "year": 1804,
     "headline": "Napoleon Crowns Himself Emperor (1804)",
     "prompt_base": "A compact powerful man in magnificent imperial robes taking a crown and placing it upon his own head in a grand cathedral, thousands of onlookers, grandiose pageantry, a pope watching"},
    {"id": "h_030", "year": 1815,
     "headline": "Napoleon Defeated at Waterloo (1815)",
     "prompt_base": "The Battle of Waterloo at its decisive moment, a commander on horseback pointing toward enemy lines, cannon smoke across Belgian fields, the French Old Guard making their last stand"},
    {"id": "h_031", "year": 1833,
     "headline": "Slavery Abolished in the British Empire (1833)",
     "prompt_base": "Formerly enslaved people celebrating their freedom on a tropical island, broken chains on the ground, families embracing, dawn breaking over a new era, emotional and powerful scene"},
    {"id": "h_032", "year": 1848,
     "headline": "Revolutions of 1848 Sweep Europe",
     "prompt_base": "Revolutionary barricades in a European city, citizens with muskets and tricolor flags, students and workers side by side, soldiers hesitating, the spirit of liberty sweeping the continent"},
    {"id": "h_033", "year": 1859,
     "headline": "Darwin Publishes On the Origin of Species (1859)",
     "prompt_base": "A naturalist in his study surrounded by fossils and biological specimens, his manuscript on the desk, the Tree of Life sketched on paper, exotic animals from his voyage, Victorian England"},
    {"id": "h_034", "year": 1865,
     "headline": "American Civil War Ends (1865)",
     "prompt_base": "Union and Confederate soldiers laying down their arms at a courthouse, officers shaking hands, exhausted men on both sides, the American flag raised over the scene, war-torn landscape at peace"},
    {"id": "h_035", "year": 1871,
     "headline": "The German Empire Proclaimed at Versailles (1871)",
     "prompt_base": "A new emperor being proclaimed in the Hall of Mirrors at Versailles, military officers celebrating, Prussian flags, the opulent golden mirrored hall, triumph after the Franco-Prussian War"},
    {"id": "h_036", "year": 1886,
     "headline": "The Statue of Liberty Unveiled (1886)",
     "prompt_base": "The Statue of Liberty unveiled in New York Harbor for the first time, ships firing celebratory salutes, confetti, crowds on the shore, patriotic atmosphere, the torch raised high"},
    {"id": "h_037", "year": 1895,
     "headline": "First Public Film Screening by the Lumière Brothers (1895)",
     "prompt_base": "The first cinema audience in Paris, gaslit salon, Victorian-dressed people watching a moving image on a white screen in shock and wonder, inventors operating their cinematograph, magic of cinema"},
    # ── 1900–1945 ──
    {"id": "h_038", "year": 1903,
     "headline": "Wright Brothers Achieve First Powered Flight (1903)",
     "prompt_base": "A fragile biplane lifting off from sandy coastal dunes at grey dawn, the pilot lying prone on the lower wing, his brother running alongside, witnesses watching in awe, a historic 12-second moment"},
    {"id": "h_039", "year": 1905,
     "headline": "Einstein Publishes Special Relativity (1905)",
     "prompt_base": "A young genius at a patent office desk, swirling equations and visions of light beams and trains around him, the universe bending, clocks melting slightly, the moment physics changed forever"},
    {"id": "h_040", "year": 1912,
     "headline": "The RMS Titanic Sinks (1912)",
     "prompt_base": "An enormous ocean liner sinking stern-first into the dark North Atlantic at night, lifeboats pulling away, stars reflected in the still water, the ship going vertical, a night of tragedy"},
    {"id": "h_041", "year": 1914,
     "headline": "Assassination of Archduke Franz Ferdinand (1914)",
     "prompt_base": "A royal motorcade on a narrow Sarajevo street, shocked bystanders, the moment of crisis that set the world on fire, crowds in early 20th-century dress, a city on a fateful summer day"},
    {"id": "h_042", "year": 1917,
     "headline": "The Russian Revolution (1917)",
     "prompt_base": "Bolshevik revolutionaries storming the Winter Palace in Petrograd, red flags waving, armed workers and soldiers, a leader on a balcony addressing massive crowds, the old world collapsing"},
    {"id": "h_043", "year": 1928,
     "headline": "Alexander Fleming Discovers Penicillin (1928)",
     "prompt_base": "A scientist in a cluttered London laboratory peering through a magnifying glass at a petri dish, a miraculous mold killing surrounding bacteria, the discovery that would save hundreds of millions of lives"},
    {"id": "h_044", "year": 1929,
     "headline": "Wall Street Crash Triggers the Great Depression (1929)",
     "prompt_base": "Panicked stockbrokers on the floor of a stock exchange, ticker tape everywhere, desperate men on telephones, the financial world in chaos, crowds forming lines outside banks, economic storm clouds"},
    {"id": "h_045", "year": 1939,
     "headline": "World War II Begins (1939)",
     "prompt_base": "Military vehicles crossing a national border at dawn, aircraft overhead, soldiers in 1939 uniforms advancing, a nation unprepared for what's coming, the beginning of the most devastating conflict ever"},
    {"id": "h_046", "year": 1944,
     "headline": "D-Day: Allied Invasion of Normandy (1944)",
     "prompt_base": "Thousands of Allied troops wading from landing craft onto a beach under fire, warships in the channel, explosions along the coast, soldiers charging forward through the surf, the liberation of Europe begins"},
    {"id": "h_047", "year": 1945,
     "headline": "Atomic Bomb Dropped on Hiroshima (1945)",
     "prompt_base": "A towering mushroom cloud rising over a Japanese city, the Enola Gay bomber visible in the distance, the awesome and terrible power of a new age, a turning point in human history, dramatic sky"},
    {"id": "h_048", "year": 1945,
     "headline": "The United Nations Founded (1945)",
     "prompt_base": "Representatives of many nations gathered in a grand American opera house to sign a world peace charter, flags of all nations displayed, a vision of international cooperation after devastating war"},
    # ── 1945–1990 ──
    {"id": "h_049", "year": 1947,
     "headline": "India Gains Independence from Britain (1947)",
     "prompt_base": "A vast joyful crowd celebrating independence, a new tricolor flag being raised for the first time, a thin elderly leader in white watching with quiet satisfaction, a new nation born at midnight"},
    {"id": "h_050", "year": 1953,
     "headline": "Hillary and Tenzing Summit Mount Everest (1953)",
     "prompt_base": "Two climbers in oxygen masks and heavy gear at the highest point on Earth, flags of their nations raised, Himalayan peaks spreading below them, brilliant sun on snow and ice, the roof of the world"},
    {"id": "h_051", "year": 1953,
     "headline": "DNA Double Helix Structure Discovered (1953)",
     "prompt_base": "Scientists in a Cambridge laboratory with their spiral molecular model, the double helix of life rising before them, X-ray crystallography images on a lightboard, a breakthrough that unlocked biology"},
    {"id": "h_052", "year": 1957,
     "headline": "Sputnik Launches the Space Age (1957)",
     "prompt_base": "A small metallic sphere with four antennae beeping as it orbits Earth in the vast starfield, a Soviet rocket launch pad below, scientists celebrating in mission control, the dawn of the Space Age"},
    {"id": "h_053", "year": 1963,
     "headline": "JFK Assassinated in Dallas (1963)",
     "prompt_base": "A presidential motorcade on a sunny American street, shocked Secret Service agents reacting, stunned crowds, 1960s cars and storefronts, the moment America's confidence shattered, a city in grief"},
    {"id": "h_054", "year": 1968,
     "headline": "Martin Luther King Jr. Assassinated (1968)",
     "prompt_base": "Mourners gathering to honor a civil rights leader, peaceful marchers carrying signs, 1960s American streets, the tragedy that galvanized a movement, candles and flowers, a nation in sorrow"},
    {"id": "h_055", "year": 1969,
     "headline": "Apollo 11: First Moon Landing (1969)",
     "prompt_base": "An astronaut in a white spacesuit descending a ladder onto the lunar surface, the American flag planted, Earth visible as a small blue marble in the black sky, bootprints in grey moon dust"},
    {"id": "h_056", "year": 1979,
     "headline": "Iranian Revolution Overthrows the Shah (1979)",
     "prompt_base": "Millions of Iranians flooding the streets of Tehran, revolutionary banners raised, the Shah's statues being toppled, an ancient nation transforming in a tidal wave of popular revolution"},
    {"id": "h_057", "year": 1986,
     "headline": "Chernobyl Nuclear Disaster (1986)",
     "prompt_base": "A nuclear reactor building in Ukraine at night, emergency vehicles arriving in darkness, a haunting blue glow of radiation, the abandoned control room, a ghost town evacuating, eerie atmosphere"},
    {"id": "h_058", "year": 1989,
     "headline": "The Berlin Wall Falls (1989)",
     "prompt_base": "Jubilant crowds at a concrete wall, people swinging hammers and pickaxes, East and West citizens embracing on top, searchlights and cranes, the Brandenburg Gate visible, champagne and tears of joy"},
    {"id": "h_059", "year": 1989,
     "headline": "Tiananmen Square: The Tank Man (1989)",
     "prompt_base": "A lone figure standing before a line of military tanks on a wide Beijing boulevard, the Great Hall of the People in the background, an act of quiet defiance that became an icon of resistance"},
    # ── 1990–2010 ──
    {"id": "h_060", "year": 1990,
     "headline": "Nelson Mandela Released from Prison (1990)",
     "prompt_base": "A dignified elderly man emerging from prison gates, fist raised in triumph, a jubilant crowd cheering, ANC flags waving, the moment that changed South Africa forever, joy and hope in the air"},
    {"id": "h_061", "year": 1991,
     "headline": "Soviet Union Dissolves (1991)",
     "prompt_base": "The hammer and sickle flag being lowered from the Kremlin at midnight, replaced by a new tricolor, Moscow crowds watching in disbelief, snow falling, the end of a superpower, history turning"},
    {"id": "h_062", "year": 1994,
     "headline": "Nelson Mandela Elected President of South Africa (1994)",
     "prompt_base": "A beloved leader being inaugurated as president, jubilant supporters in colorful traditional dress, military jets flying overhead in formation, a rainbow nation celebrating its first free election"},
    {"id": "h_063", "year": 2001,
     "headline": "September 11 Terrorist Attacks (2001)",
     "prompt_base": "The New York City skyline shrouded in smoke, emergency vehicles below, people on streets looking upward in disbelief, American flags, a city in shock and grief, a moment that changed the world"},
    {"id": "h_064", "year": 2004,
     "headline": "Indian Ocean Tsunami (2004)",
     "prompt_base": "A massive wave overwhelming a peaceful tropical coastline, palm trees bending, villages flooded, rescue boats arriving in the aftermath, the devastating power of nature, humanitarian response"},
    {"id": "h_065", "year": 2008,
     "headline": "Barack Obama Elected First Black US President (2008)",
     "prompt_base": "An elegant African-American family on a stage before a massive jubilant crowd in Chicago's Grant Park at night, confetti falling, a historic election night, America making history"},
    # ── Extras ──
    {"id": "h_066", "year": 1683,
     "headline": "Ottoman Siege of Vienna Repelled (1683 AD)",
     "prompt_base": "Winged cavalry charging down a hillside into Ottoman siege lines around a great Central European city, crescent and cross banners clashing, the decisive moment that stopped Ottoman expansion into Europe"},
    {"id": "h_067", "year": 1368,
     "headline": "The Ming Dynasty Founded in China (1368 AD)",
     "prompt_base": "A new emperor in magnificent imperial dragon robes seated on the Dragon Throne, the Forbidden City under construction behind him, thousands of soldiers kneeling in ceremony, a new Chinese dynasty begins"},
    {"id": "h_068", "year": 1687,
     "headline": "Ottoman Empire at Its Greatest Extent (1680s AD)",
     "prompt_base": "A magnificent Ottoman sultan surveying his vast empire from a palace balcony overlooking Constantinople, the Bosphorus below, minarets glinting in sunlight, a court of scholars and military commanders"},
    {"id": "h_069", "year": 1789,
     "headline": "The First Hot Air Balloon Crosses the English Channel (1785)",
     "prompt_base": "A colorful hot air balloon floating over the cliffs of Dover toward the French coast, crowds watching from English and French shores, blue sky and white clouds, the wonder of early aviation"},
    {"id": "h_070", "year": 1815,
     "headline": "The Congress of Vienna Redraws Europe (1815)",
     "prompt_base": "Elegantly dressed diplomats and monarchs gathered around a great map-covered table in a Viennese palace, redrawing the borders of Europe after Napoleon, the balance of power being negotiated"},
    {"id": "h_071", "year": 1896,
     "headline": "First Modern Olympic Games in Athens (1896)",
     "prompt_base": "Athletes from many nations competing in the marble Panathinaiko Stadium in Athens under the bright Greek sun, the Olympic rings not yet invented, ancient and modern worlds meeting, inaugural glory"},
    {"id": "h_072", "year": 1969,
     "headline": "Woodstock Music Festival (1969)",
     "prompt_base": "Half a million young people at a vast outdoor concert in upstate New York, peace signs and flowers, musicians on a distant stage, tents and muddy fields as far as the eye can see, the spirit of a generation"},
]

# ─────────────────────────────────────────────────────────────
# ART STYLES POOL  (~22 styles for history images)
# ─────────────────────────────────────────────────────────────
ART_STYLES = [
    {"id": "bosch",        "name": "Hieronymus Bosch",
     "suffix": "in the surreal fantastical style of Hieronymus Bosch — intricate bizarre creatures, hellscapes, dense symbolic detail, medieval Dutch oil painting"},
    {"id": "vangogh",      "name": "Vincent van Gogh",
     "suffix": "in the post-impressionist style of Van Gogh — swirling expressive brushstrokes, vibrant colors, thick impasto paint, emotional intensity, oil painting"},
    {"id": "monet",        "name": "Claude Monet",
     "suffix": "in the Impressionist style of Monet — soft broken brushstrokes, dappled light, pastel palette, atmospheric haze capturing a fleeting moment, oil painting"},
    {"id": "friedrich",    "name": "Caspar David Friedrich",
     "suffix": "in the Romantic style of Caspar David Friedrich — solitary figures against vast sublime landscapes, misty atmosphere, dramatic skies, existential wonder, oil painting"},
    {"id": "picasso",      "name": "Pablo Picasso (Cubism)",
     "suffix": "in Picasso's Cubist style — fragmented geometric forms showing multiple perspectives simultaneously, bold outlines, abstract deconstruction of the subject, oil painting"},
    {"id": "dali",         "name": "Salvador Dalí (Surrealism)",
     "suffix": "in Dalí's Surrealist style — dreamlike melting objects, impossible architecture, hyper-realistic rendering of irrational scenes, subconscious imagery, oil painting"},
    {"id": "rembrandt",    "name": "Rembrandt van Rijn",
     "suffix": "in the Dutch Golden Age style of Rembrandt — dramatic chiaroscuro lighting, rich warm tones, deep psychological depth, intimate portraiture, oil painting"},
    {"id": "ukiyoe",       "name": "Japanese Ukiyo-e",
     "suffix": "as a Japanese Ukiyo-e woodblock print — bold black outlines, flat areas of vivid color, graceful flowing lines, Mt. Fuji or wave motifs, Edo period aesthetics"},
    {"id": "illuminated",  "name": "Medieval Illuminated Manuscript",
     "suffix": "as a medieval illuminated manuscript page — gold leaf accents, intricate decorative borders, flat perspective, vivid pigments, Gothic lettering surrounding the scene"},
    {"id": "propaganda",   "name": "Soviet Constructivist Poster",
     "suffix": "as a Soviet constructivist propaganda poster — bold geometric shapes, strong diagonal composition, limited red-white-black palette, heroic stylized figures, constructivist typography"},
    {"id": "artdeco",      "name": "Art Deco",
     "suffix": "in the Art Deco style — geometric symmetry, gold and black metallic tones, streamlined elegance, sunburst patterns, the glamour of 1920s-30s graphic illustration"},
    {"id": "comic",        "name": "Classic Comic Book",
     "suffix": "as a dramatic classic comic book panel — Ben-Day dots, bold black ink outlines, speech bubbles, dynamic action angles, sound-effect lettering, primary color heroic illustration"},
    {"id": "hyperreal",    "name": "Hyperrealistic Photography",
     "suffix": "as an extremely detailed hyperrealistic photograph — perfect documentary lighting, photojournalistic composition, sharp focus, stunning visual clarity, as if actually captured"},
    {"id": "watercolor",   "name": "Watercolor Illustration",
     "suffix": "as a delicate watercolor illustration — soft wet-on-wet washes, bleeding edges, translucent layers of pigment, luminous whites, gentle poetic atmosphere"},
    {"id": "artnouveau",   "name": "Art Nouveau (Mucha)",
     "suffix": "in the Art Nouveau style of Alphonse Mucha — flowing organic lines, decorative floral borders, elegant elongated figures, soft pastel colors, intricate ornamental detail"},
    {"id": "banksy",       "name": "Banksy Street Art",
     "suffix": "as a Banksy-style street art stencil — stark black and white spray paint, subversive wit, brick wall texture, guerrilla art aesthetic, political commentary through irony"},
    {"id": "baroque",      "name": "Baroque (Caravaggio)",
     "suffix": "in the Baroque style of Caravaggio — extreme dramatic chiaroscuro, theatrical single-source lighting against deep shadow, intense emotional realism, dynamic composition, oil painting"},
    {"id": "cyberpunk",    "name": "Cyberpunk Futurism",
     "suffix": "reimagined as a neon-lit cyberpunk scene — holographic displays, rain-soaked dark streets, glowing neon signs, futuristic megastructures, dystopian high-tech atmosphere"},
    {"id": "renaissance",  "name": "High Renaissance (Raphael)",
     "suffix": "in the High Renaissance style of Raphael — idealized classical figures, balanced harmonious composition, sfumato atmospheric perspective, divine humanist beauty, fresco"},
    {"id": "expressionism","name": "Expressionism (Edvard Munch)",
     "suffix": "in the Expressionist style of Edvard Munch — distorted anguished figures, swirling emotional landscapes, psychologically intense color, raw inner torment, oil painting"},
    {"id": "klimt",        "name": "Gustav Klimt",
     "suffix": "in the style of Gustav Klimt — ornate gold leaf patterns, Byzantine mosaic-like decoration, sensual elongated figures, intricate geometric and floral motifs, Viennese Symbolism"},
    {"id": "retro_poster", "name": "Retro Travel Poster",
     "suffix": "as a 1930s-1950s retro travel poster — bold flat colors, simplified shapes, optimistic sunny atmosphere, art deco typography, vintage graphic design nostalgia"},
]

# ─────────────────────────────────────────────────────────────
# IMAGE GENERATION — DALL-E 3 (Germany, World, Collage)
# ─────────────────────────────────────────────────────────────
def generate_image(prompt, filename):
    url = "https://api.openai.com/v1/images/generations"
    data = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "quality": "standard",
        "response_format": "b64_json"
    }).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req, timeout=90) as resp:
        result = json.loads(resp.read())
    img_b64 = result["data"][0]["b64_json"]
    img_bytes = base64.b64decode(img_b64)
    out_path = os.path.join(OUT_DIR, filename)
    with open(out_path, "wb") as f:
        f.write(img_bytes)
    print(f"  ✅ Saved {filename} ({len(img_bytes)//1024}KB)")
    return f"images/{filename}"

# ─────────────────────────────────────────────────────────────
# IMAGE GENERATION — Replicate Flux Schnell (History)
# Cheaper than DALL-E 3, great artistic quality, fast (~3s)
# Falls back to DALL-E if REPLICATE_API_TOKEN is not set.
# ─────────────────────────────────────────────────────────────
def generate_image_replicate(prompt, filename):
    """Generate via Replicate Flux Schnell API. Falls back to DALL-E if no token."""
    import time

    if not REPLICATE_API_TOKEN:
        print("  ⚠️  REPLICATE_API_TOKEN not set — falling back to DALL-E 3")
        return generate_image(prompt, filename)

    url = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
    data = json.dumps({
        "input": {
            "prompt": prompt,
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "output_format": "png",
            "num_inference_steps": 4
        }
    }).encode()

    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
        "Prefer": "wait"   # synchronous response (up to 60s)
    })

    with urllib.request.urlopen(req, timeout=90) as resp:
        result = json.loads(resp.read())

    # Poll if still processing (Prefer:wait may time out on busy servers)
    if result.get("status") in ("starting", "processing"):
        poll_url = result.get("urls", {}).get("get", "")
        for _ in range(30):
            time.sleep(3)
            req2 = urllib.request.Request(poll_url, headers={
                "Authorization": f"Bearer {REPLICATE_API_TOKEN}"
            })
            with urllib.request.urlopen(req2, timeout=30) as r2:
                result = json.loads(r2.read())
            if result.get("status") == "succeeded":
                break
        else:
            raise Exception("Replicate polling timeout")

    if result.get("status") != "succeeded":
        raise Exception(f"Replicate error: {result.get('error', 'unknown')}")

    output = result.get("output", [])
    if not output:
        raise Exception("Replicate returned no output")

    img_url = output[0] if isinstance(output, list) else output
    with urllib.request.urlopen(img_url, timeout=60) as resp:
        img_bytes = resp.read()

    out_path = os.path.join(OUT_DIR, filename)
    with open(out_path, "wb") as f:
        f.write(img_bytes)
    print(f"  ✅ Saved {filename} via Flux/Replicate ({len(img_bytes)//1024}KB)")
    return f"images/{filename}"

# ─────────────────────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────────────────────
os.makedirs(OUT_DIR, exist_ok=True)
today = datetime.date.today().isoformat()

# ─────────────────────────────────────────────────────────────
# ARCHIVE YESTERDAY'S QUIZ
# ─────────────────────────────────────────────────────────────
if os.path.exists(JSON_PATH):
    try:
        with open(JSON_PATH) as f:
            old = json.load(f)
        old_date = old.get("date", "")
        if old_date and old_date != today:
            archive_dir = os.path.join(OUT_DIR, old_date)
            os.makedirs(archive_dir, exist_ok=True)
            # Copy + relink category images (germany, world, history)
            for items in old.get("categories", {}).values():
                for item in items:
                    src = os.path.join(WEBROOT, item["image"])
                    if os.path.exists(src):
                        fname = os.path.basename(src)
                        shutil.copy2(src, os.path.join(archive_dir, fname))
                        item["image"] = f"images/{old_date}/{fname}"
            # Copy + relink collage images
            for styles in old.get("collages", {}).values():
                for info in styles.values():
                    src = os.path.join(WEBROOT, info["image"])
                    if os.path.exists(src):
                        fname = os.path.basename(src)
                        shutil.copy2(src, os.path.join(archive_dir, fname))
                        info["image"] = f"images/{old_date}/{fname}"
            # Copy + relink On This Day images
            if old.get("onthisday"):
                for item in old["onthisday"].get("events", []):
                    src = os.path.join(WEBROOT, item["image"])
                    if os.path.exists(src):
                        fname = os.path.basename(src)
                        shutil.copy2(src, os.path.join(archive_dir, fname))
                        item["image"] = f"images/{old_date}/{fname}"
            # Write archived quiz-data-YYYY-MM-DD.json
            archive_json = os.path.join(WEBROOT, f"quiz-data-{old_date}.json")
            with open(archive_json, "w") as f:
                json.dump(old, f, indent=2, ensure_ascii=False)
            # Update archive-index.json
            index_path = os.path.join(WEBROOT, "archive-index.json")
            index = json.load(open(index_path)) if os.path.exists(index_path) else []
            if old_date not in index:
                index.insert(0, old_date)
            with open(index_path, "w") as f:
                json.dump(index, f)
            print(f"✅ Archived {old_date} → images/{old_date}/ + quiz-data-{old_date}.json")
    except Exception as e:
        print(f"⚠️  Archive skipped: {e}")

# ─────────────────────────────────────────────────────────────
# GENERATE GERMANY + WORLD CATEGORY IMAGES
# ─────────────────────────────────────────────────────────────
quiz_categories = {}
for cat_key, items in CATEGORIES.items():
    quiz_items = []
    for item in items:
        filename = f"{item['id']}.png"
        out_path = os.path.join(OUT_DIR, filename)
        if os.path.exists(out_path):
            print(f"  ⏭  {filename} already exists, skipping")
            quiz_items.append({"id": item["id"], "headline": item["headline"], "source": item["source"], "image": f"images/{filename}"})
            continue
        print(f"\n🖼  [{cat_key.upper()}] {item['headline'][:55]}...")
        try:
            image_path = generate_image(item["prompt"], filename)
            quiz_items.append({"id": item["id"], "headline": item["headline"], "source": item["source"], "image": image_path})
        except Exception as e:
            print(f"  ❌ Error: {e}")
    quiz_categories[cat_key] = quiz_items

# ─────────────────────────────────────────────────────────────
# GENERATE HISTORY CATEGORY IMAGES
# Seed by date so same day always gives same events + styles
# ─────────────────────────────────────────────────────────────
date_seed = int(hashlib.md5(today.encode()).hexdigest(), 16) % (2**32)
rng = random.Random(date_seed)

# Pick 8 events: first 4 get images, next 4 are distractors (decoys)
shuffled_events = rng.sample(HISTORICAL_EVENTS, min(8, len(HISTORICAL_EVENTS)))
history_main       = shuffled_events[:4]
history_distractors = shuffled_events[4:8]

history_items = []
for i, event in enumerate(history_main):
    style = rng.choice(ART_STYLES)
    filename = f"hi{i+1}.png"
    out_path = os.path.join(OUT_DIR, filename)
    if os.path.exists(out_path):
        print(f"  ⏭  {filename} already exists, skipping")
        # Reconstruct metadata (style may differ if script re-runs after a crash)
        # Use stored quiz-data.json if available, else best-effort
        history_items.append({
            "id": f"hi{i+1}", "headline": event["headline"],
            "year": event["year"], "source": "Historical Record",
            "style": style["name"], "image": f"images/{filename}"
        })
        continue
    full_prompt = f"{event['prompt_base']}, {style['suffix']}, highly detailed, award-winning composition"
    print(f"\n🏛️  [HISTORY via Replicate/Flux] {event['headline'][:50]}... [{style['name']}]")
    try:
        image_path = generate_image_replicate(full_prompt, filename)
        history_items.append({
            "id": f"hi{i+1}", "headline": event["headline"],
            "year": event["year"], "source": "Historical Record",
            "style": style["name"], "image": image_path
        })
    except Exception as e:
        print(f"  ❌ Error: {e}")

history_distractor_items = [
    {"id": f"hd{i+1}", "headline": ev["headline"],
     "year": ev["year"], "source": "Historical Record"}
    for i, ev in enumerate(history_distractors)
]
quiz_categories["history"] = history_items

# ─────────────────────────────────────────────────────────────
# GENERATE "ON THIS DAY" IMAGES (Wikipedia API)
# ─────────────────────────────────────────────────────────────
def fetch_onthisday_events():
    """Fetch events from Wikipedia's On This Day API for today's date."""
    month = datetime.date.today().month
    day = datetime.date.today().day
    url = f"https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/events/{month:02d}/{day:02d}"
    
    req = urllib.request.Request(url, headers={
        'User-Agent': 'AINewsQuizBot/1.0 (OpenClaw; shelldon@professionalcrastination.de)'
    })
    
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    
    return data['events']

def select_otd_events(events):
    """Select 4 main + 4 distractor events with visual potential."""
    # Filter for events 500-2020 with pages/thumbnails
    interesting = []
    for evt in events:
        year = evt.get('year', 0)
        text = evt.get('text', '')
        pages = evt.get('pages', [])
        
        if 500 <= year <= 2020 and len(pages) > 0:
            # Score based on visual/historical keywords
            keywords = ['emperor', 'king', 'queen', 'war', 'battle', 'discovered', 'founded',
                       'independence', 'revolution', 'treaty', 'expedition', 'crowned',
                       'built', 'conquest', 'marines', 'landing', 'attack', 'invasion',
                       'signed', 'declared', 'assassinated', 'born', 'died']
            score = sum(1 for kw in keywords if kw.lower() in text.lower())
            interesting.append({
                'year': year,
                'text': text,
                'pages': pages,
                'score': score
            })
    
    # Sort by score and year (prefer diverse time periods)
    interesting.sort(key=lambda x: (x['score'], -x['year']), reverse=True)
    
    # Select 8 events spread across centuries
    selected = []
    used_centuries = set()
    
    for evt in interesting:
        century = evt['year'] // 100
        if century not in used_centuries or len(selected) >= 4:
            selected.append(evt)
            used_centuries.add(century)
            if len(selected) == 8:
                break
    
    # If we need more, add highest-scoring remaining
    if len(selected) < 8:
        for evt in interesting:
            if evt not in selected:
                selected.append(evt)
                if len(selected) == 8:
                    break
    
    return selected[:4], selected[4:8]  # (main, distractors)

def create_otd_prompt(text, year):
    """Create an AI image prompt from Wikipedia event text."""
    # Clean up the text (remove references, excessive detail)
    clean_text = text.split('.')[0]  # First sentence usually most important
    
    # Create a descriptive prompt based on the event
    prompt = f"Historical scene from the year {year}: {clean_text}, "
    prompt += "dramatic historical painting, photorealistic editorial illustration, "
    prompt += "highly detailed, award-winning composition, cinematic lighting"
    
    return prompt

# Generate On This Day quiz data
otd_items = []
otd_distractor_items = []

try:
    print("\n🗓️  FETCHING 'ON THIS DAY' EVENTS FROM WIKIPEDIA...")
    all_events = fetch_onthisday_events()
    print(f"   Found {len(all_events)} total events for {today}")
    
    main_events, distractor_events = select_otd_events(all_events)
    print(f"   Selected {len(main_events)} main events + {len(distractor_events)} distractors\n")
    
    # Generate images for the 4 main events
    for i, evt in enumerate(main_events):
        style = rng.choice(ART_STYLES)
        filename = f"otd{i+1}.png"
        out_path = os.path.join(OUT_DIR, filename)
        
        # Create headline from event text
        headline_text = evt['text'].split('.')[0]  # First sentence
        if len(headline_text) > 100:
            headline_text = headline_text[:97] + "..."
        
        if os.path.exists(out_path):
            print(f"  ⏭  {filename} already exists, skipping")
            otd_items.append({
                "id": f"otd{i+1}",
                "headline": headline_text,
                "year": evt['year'],
                "source": "Wikipedia",
                "style": style["name"],
                "image": f"images/{filename}"
            })
            continue
        
        # Create prompt
        base_prompt = create_otd_prompt(evt['text'], evt['year'])
        full_prompt = f"{base_prompt}, {style['suffix']}, highly detailed, award-winning composition"
        
        print(f"🗓️  [ON THIS DAY via Replicate/Flux] Year {evt['year']}: {headline_text[:60]}... [{style['name']}]")
        
        try:
            image_path = generate_image_replicate(full_prompt, filename)
            otd_items.append({
                "id": f"otd{i+1}",
                "headline": headline_text,
                "year": evt['year'],
                "source": "Wikipedia",
                "style": style["name"],
                "image": image_path
            })
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Create distractor items (no images)
    for i, evt in enumerate(distractor_events):
        headline_text = evt['text'].split('.')[0]
        if len(headline_text) > 100:
            headline_text = headline_text[:97] + "..."
        
        otd_distractor_items.append({
            "id": f"otdd{i+1}",
            "headline": headline_text,
            "year": evt['year'],
            "source": "Wikipedia"
        })
    
    print(f"\n✅ Generated {len(otd_items)} On This Day images")
    print(f"   Years: {[it['year'] for it in otd_items]}")
    print(f"   Styles: {[it['style'] for it in otd_items]}")

except Exception as e:
    print(f"\n⚠️  Failed to generate On This Day content: {e}")
    print("   Continuing without otd data...")

# ─────────────────────────────────────────────────────────────
# GENERATE COLLAGE IMAGES
# ─────────────────────────────────────────────────────────────
quiz_collages = {}
for cat_key, styles in COLLAGE_PROMPTS.items():
    quiz_collages[cat_key] = {}
    for style_key, info in styles.items():
        filename = f"collage_{cat_key}_{style_key}.png"
        out_path = os.path.join(OUT_DIR, filename)
        if os.path.exists(out_path):
            print(f"  ⏭  {filename} already exists, skipping")
            quiz_collages[cat_key][style_key] = {"image": f"images/{filename}", "style": info["style"]}
            continue
        print(f"\n🎨  [COLLAGE {cat_key.upper()} / {style_key.upper()}] generating...")
        try:
            image_path = generate_image(info["prompt"], filename)
            quiz_collages[cat_key][style_key] = {"image": image_path, "style": info["style"]}
        except Exception as e:
            print(f"  ❌ Error: {e}")

# ─────────────────────────────────────────────────────────────
# WRITE quiz-data.json
# ─────────────────────────────────────────────────────────────
quiz_data = {
    "date": today,
    "categories": quiz_categories,
    "distractors": {"history": history_distractor_items},
    "collages": quiz_collages
}

# Add On This Day data if we generated it
if otd_items:
    quiz_data["onthisday"] = {
        "date": today,  # Store as YYYY-MM-DD for display
        "events": otd_items,
        "distractors": otd_distractor_items
    }
with open(JSON_PATH, "w") as f:
    json.dump(quiz_data, f, indent=2, ensure_ascii=False)

print(f"\n✅ quiz-data.json written to {JSON_PATH}")
print(f"   Categories: {list(quiz_categories.keys())} ({len(history_items)} history events)")
print(f"   History styles today: {[it.get('style','?') for it in history_items]}")
print(f"   Collages: {list(quiz_collages.keys())}")
