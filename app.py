import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="Health-Promoting Spaces Scorer",
    layout="wide",
    page_icon="🏥",
)

# Streamlit drops widget state when the widget isn't on the current page.
# Re-binding each saved answer to itself preserves it across navigation.
for _k in list(st.session_state.keys()):
    if _k.startswith(("A_", "B_", "C_", "D_", "E_")):
        st.session_state[_k] = st.session_state[_k]

# ============================================================
# Question type constants
# ============================================================
TYPE_YESNO = "yesno"
TYPE_YESNO_IDK = "yesno_idk"
TYPE_YESNO_NA = "yesno_na"
TYPE_MULTI = "multi"
TYPE_GRADED = "graded"
TYPE_SCREENING = "screening"           # Yes / No
TYPE_SCREENING_NA = "screening_na"     # Yes / No / N/A

# Convention for graded options:
# {"label": str, "score": float | None}  — score=None means "excluded"

# ============================================================
# Assessment definition: 5 categories
# Question IDs are prefixed with the category letter to avoid collisions.
# ============================================================
CATEGORIES = [
    # =========================================================
    # CATEGORY A — FUNCTIONALITY
    # =========================================================
    {
        "id": "A",
        "name": "Functionality",
        "attributes": [
            {
                "id": "1", "name": "Location & Connectivity",
                "indicators": [
                    {
                        "id": "1.1", "name": "Walkability – Daily Needs",
                        "questions": [{
                            "qid": "A_Q1", "type": TYPE_MULTI,
                            "text": "Are the following daily services or amenities accessible within approximately a 5–6-minute walking distance from the main building entrance?",
                            "sub_items": [
                                "Public transit stops (e.g., bus, train, metro, or tram)",
                                "Food access point (e.g., supermarket, grocery store, fresh food market, café or restaurant for daily meals)",
                                "Financial service (e.g., bank, ATM)",
                                "Healthcare provider (e.g., clinic, primary care center, pharmacy, hospital)",
                                "Care or education facility (e.g., childcare, school, adult day care, elderly care services)",
                                "Essential goods and services retail (e.g., hardware store, basic household goods, post office, repair services, neighborhood marketplace)",
                            ],
                        }],
                    },
                    {
                        "id": "1.2", "name": "Walkability – Physical Activity & Recreation",
                        "questions": [{
                            "qid": "A_Q2", "type": TYPE_MULTI,
                            "text": "Are the following physical activities or recreational amenities accessible within approximately a 5–6-minute walking distance from the main building entrance?",
                            "sub_items": [
                                "Public outdoor green space (e.g., parks, plazas, pedestrian zones with tree-planted areas with benches for rest; sidewalks don’t apply)",
                                "Sports and physical activity facilities (e.g., gyms, fitness centers, sports courts, swimming pools, dance or movement studios, outdoor exercise areas)",
                            ],
                        }],
                    },
                    {
                        "id": "1.3", "name": "Pedestrian priority measures",
                        "questions": [{
                            "qid": "A_Q3", "type": TYPE_MULTI,
                            "text": "Are any of the following pedestrian safety and traffic calming measures implemented near the building?",
                            "sub_items": [
                                "Lower speed limits are implemented in more than half of the street segments within approximately a 5–6-minute walking distance (≈400 m) from the main entrance (e.g., posted speed limit of 30 km/h or less)",
                                "Pedestrian priority measures are implemented in more than half of nearby intersections within approximately a 5–6-minute walking distance (~400 m) from the main entrance (e.g., raised crossings, widened sidewalks, pedestrian-priority signals, traffic calming elements such as traffic lights, stop signs, or reduced vehicle dominance)",
                                "Continuous physical buffers are provided along pedestrian and/or bicycle routes connecting to the building entrance(s) (e.g., protected bike lanes, tree rows, or planter barriers separating users from vehicle traffic)",
                            ],
                        }],
                    },
                    {
                        "id": "1.4", "name": "Safe and accessible arrival",
                        "questions": [{
                            "qid": "A_Q4", "type": TYPE_MULTI,
                            "text": "How does the building support safe and accessible arrival and access for all users? Indicate whether the following conditions are met.",
                            "sub_items": [
                                "Safe drop-off or pick-up areas are provided where relevant to the building type (excluding schools) (e.g., healthcare facilities, elderly care, or buildings serving vulnerable users)",
                                "Pedestrian access routes from the street to the building entrance are safe and accessible (e.g., step-free access, clear paths, appropriate crossings or separation from vehicle traffic)",
                                "Arrival areas are designed to minimize conflicts between pedestrians, cyclists, and vehicles (e.g., clear circulation paths, or designated zones)",
                            ],
                        }],
                    },
                    {
                        "id": "1.5", "name": "Bicycle / Micromobility parking",
                        "questions": [{
                            "qid": "A_Q5", "type": TYPE_YESNO,
                            "text": "Is there convenient parking for bicycles and micromobility devices (scooters, e-scooters) near the main entrance (within approximately 30 m), either provided by the building or available in the immediate public realm?",
                        }],
                    },
                    {
                        "id": "1.6", "name": "Bicycle routes",
                        "questions": [
                            {"qid": "A_Q6", "type": TYPE_SCREENING,
                             "text": "Are there bicycle routes within the proximity of the main building entrance?"},
                            {"qid": "A_Q7", "type": TYPE_GRADED,
                             "text": "What are the characteristics of the bicycle routes? Choose one that applies.",
                             "options": [
                                 {"label": "All the following elements are present: separate from motor vehicles; accessible directly from the building entrance; uninterrupted by driveways or vehicular crossings for the entire route to key destinations.", "score": 1.0},
                                 {"label": "Some of the following elements are present: only partially separate from motor vehicles; occasional interruptions by driveways or vehicle crossings; not continuously accessible from the main entrance.", "score": 0.5},
                                 {"label": "None of the required elements are present: existing bicycle routes do not meet basic separation and continuity requirements.", "score": 0.0},
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "2", "name": "Intersectionality",
                "indicators": [
                    {
                        "id": "2.1", "name": "Universal access – Compliance",
                        "questions": [{
                            "qid": "A_Q8", "type": TYPE_YESNO_IDK,
                            "text": "Does the building comply with the Catalan Accessibility Code (Decree 209/2023) to ensure accessibility throughout the building, including entrances, corridors, and restrooms? Select the option that applies best. (Yes: the building in-use or the project fully complies, or has been fully adapted to be universally accessible according to its typology. No: the building in-use does not comply, even if it partially complies or is in process of adaptation. I don't know: there is no way at this moment for the respondent to know if the building complies with the current Decree.)",
                        }],
                    },
                    {
                        "id": "2.2", "name": "Inclusive and safe use",
                        "questions": [{
                            "qid": "A_Q9", "type": TYPE_MULTI,
                            "text": "Does the building design support inclusive and safe use of restroom facilities and related amenities by people of different genders and needs? What characteristics are present?",
                            "sub_items": [
                                "The building provides male and female restrooms as well as a universal single-user restroom (universal restroom: fully enclosed room with toilet and sink inside, usable by any gender and by caregivers or people needing assistance)",
                                "Restroom signage clearly indicates available options (e.g., male, female, universal/all-gender, accessible) to support user choice and comfort",
                                "Changing tables are provided in locations accessible to all users (not restricted to a single gender restroom)",
                            ],
                        }],
                    },
                ],
            },
            {
                "id": "3", "name": "Wayfinding",
                "indicators": [
                    {
                        "id": "3.1", "name": "Wayfinding signage",
                        "questions": [{
                            "qid": "A_Q10", "type": TYPE_YESNO,
                            "text": "Are wayfinding signs and clear signage, as designed, available in key locations and main circulation areas to make internal navigation easier for all building users (e.g., in the main lobby, main corridors, and elevator waiting areas)?",
                        }],
                    },
                    {
                        "id": "3.2", "name": "Spatial legibility",
                        "questions": [{
                            "qid": "A_Q11", "type": TYPE_MULTI,
                            "text": "Which of the following statements best describes the building related to its spatial legibility (i.e., how easy it is to understand and navigate the layout)?",
                            "sub_items": [
                                "The space is easy to understand from the point of entry (e.g., with clear sightlines to circulation and information points and/or double-height spaces that improve orientation across floors if available)",
                                "There is use of color codes or differentiated materials to signalize doors, different zones or to distinguish floors if available",
                                "The space includes graphic landmarks positioned at the decision points (e.g., signage icons, numbers or symbols on floors or walls)",
                            ],
                        }],
                    },
                    {
                        "id": "3.3", "name": "Internal Service Directory",
                        "questions": [
                            {"qid": "A_Q12", "type": TYPE_SCREENING,
                             "text": "Does the building design include a permanent internal services directory (physical or digital display) at the main building entrance that lists services within the building to support orientation?"},
                            {"qid": "A_Q13", "type": TYPE_MULTI,
                             "text": "What are the characteristics of the internal services directory?",
                             "sub_items": [
                                 "Completeness of internal information; includes a complete overview of the building’s services and key destinations (e.g., departments, facilities, main functions)",
                                 "Clear information; includes internal navigation (a site map or information about the facility’s services and their locations)",
                                 "Easy to read and understand; uses high-contrast colors, clear layout, and legible font size",
                                 "Accessible to diverse users; includes graphic signage, braille and/or audio to facilitate usage for people with varying sensory needs",
                             ]},
                        ],
                    },
                    {
                        "id": "3.4", "name": "Nearby services directory",
                        "questions": [
                            {"qid": "A_Q14", "type": TYPE_SCREENING,
                             "text": "Does the building design include a permanent, nearby services directory (physical or digital display) at the main building entrance that lists amenities/services in the surrounding area to support orientation and access to nearby resources?"},
                            {"qid": "A_Q15", "type": TYPE_MULTI,
                             "text": "What are the characteristics of the local/neighborhood services directory?",
                             "sub_items": [
                                 "The permanent local services directory shows facilities nearby (in 5–6 minutes walkable distance) such as public transit stops, food outlets/restaurants, markets, financial facilities/banks, ATMs and the information is updated regularly",
                                 "The permanent local services directory shows nearby public outdoor spaces such as parks, public squares with seating and greenery",
                                 "The permanent local services directory uses high-contrast colors and the text is in a clear font",
                                 "The permanent local services directory includes graphic signage, braille and/or audio to facilitate usage for people with varying sensory needs",
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "4", "name": "Technology & Digitalization",
                "indicators": [
                    {
                        "id": "4.1", "name": "Digital Connectivity",
                        "questions": [{
                            "qid": "A_Q16", "type": TYPE_GRADED,
                            "text": "Which option best describes how digital connectivity is designed and implemented in the building? Choose the one that applies.",
                            "options": [
                                {"label": "Optimized Connectivity (ALARA-aligned): reliable connectivity is ensured through a balanced approach that may include wired connections, distributed low-power Wi-Fi, and strategic placement of access points to minimize unnecessary exposure while maintaining performance.", "score": 1.0},
                                {"label": "Standard Full Wi-Fi Coverage (No ALARA-Aligned): reliable Wi-Fi is available throughout most or all areas of the building, with no specific measures taken to reduce exposure or optimize transmission.", "score": 0.5},
                                {"label": "Partial or No Connectivity: Wi-Fi is available but limited to certain areas, with inconsistent performance across the building.", "score": 0.0},
                            ],
                        }],
                    },
                    {
                        "id": "4.2", "name": "Technological features",
                        "questions": [{
                            "qid": "A_Q17", "type": TYPE_YESNO,
                            "text": "Does the building design include at least one technological feature integrated to support building usability (e.g., touch-free entry, QR-coded wayfinding, or assistive audio/visual systems)?",
                        }],
                    },
                ],
            },
            {
                "id": "5", "name": "Environmental Control",
                "indicators": [
                    {
                        "id": "5.1", "name": "Environmental control features",
                        "questions": [
                            {"qid": "A_Q18", "type": TYPE_SCREENING,
                             "text": "Does the facility include regularly occupied staff or work areas? (Exclude temporary or intermittent staff such as cleaning or maintenance personnel. Staff refers to regularly present employees or occupants with dedicated work areas — e.g., office staff, healthcare workers, administrative personnel.)"},
                            {"qid": "A_Q19", "type": TYPE_MULTI,
                             "text": "Which of the following indoor environmental controls are included in the building design to allow staff to adjust and regulate their immediate environment as desired (e.g., in offices, staff rooms, or other work areas)?",
                             "sub_items": [
                                 "Individual Task Lighting: a personal desk lamp or adjustable task light at all workstations",
                                 "Operable Shading: shading on the windows (e.g., manual or electrical blinds, curtains, or other coverings) to control daylight and glare",
                                 "Personal Temperature Control: a personal or zonal control unit to adjust the temperature (e.g., a manual thermostat, an individual fan, or a personal space heater)",
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "6", "name": "Physical Activity Promotion",
                "indicators": [
                    {
                        "id": "6.1", "name": "Physical activity promoting features",
                        "questions": [{
                            "qid": "A_Q20", "type": TYPE_MULTI,
                            "text": "Which of the following facilities are included in the building design to support regular occupants/staff in promoting physical activity?",
                            "sub_items": [
                                "Bicycle racks inside the building (for staff use only)",
                                "Fitness area (small gym) within the building or 5–6 minutes’ walkable distance",
                                "Showers and lockers within the building, provided in sufficient number and capacity to accommodate staff needs",
                            ],
                        }],
                    },
                    {
                        "id": "6.2", "name": "Accessible and attractive stair design",
                        "questions": [
                            {"qid": "A_Q21", "type": TYPE_SCREENING_NA,
                             "text": "Does the building design include a stair connecting publicly accessible floors that can be used by occupants for movement between floors? (Select N/A if, e.g., the facility has only one floor.)"},
                            {"qid": "A_Q22", "type": TYPE_MULTI,
                             "text": "Which of the following design strategies for promoting stair use have been implemented in the building (excluding emergency exit stair)?",
                             "sub_items": [
                                 "Basic Access: at least one stairwell connects all publicly accessible floors (e.g., from lobby to upper floor)",
                                 "Full Building Access: at least one stairwell connects all floors of the building, from top to bottom",
                                 "Prominent Location: the main stair is located in a visible, prominent place (e.g., near elevators or the main lobby)",
                                 "Safety Enhancements: the stair environment includes high-visibility safety features applied consistently across the stair (e.g., contrasting treads, continuous handrails)",
                                 "Aesthetics: the stair environment includes at least one enhancing element (e.g., art, color, natural or artificial lighting, music) applied along the stair path",
                                 "Stair-use Encouraging Signs: stair-use encouraging signage is present at key decision points and/or stair landings in most (more than half) locations",
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "7", "name": "Ergonomics",
                "indicators": [
                    {
                        "id": "7.1", "name": "Ergonomic Design",
                        "questions": [{
                            "qid": "A_Q23", "type": TYPE_MULTI,
                            "text": "Which of the following design characteristics describes how regularly occupied spaces support ergonomic posture, comfort, and safe use? (Guidance may be found in ISO ergonomic standards, occupational health recommendations, or workplace ergonomics guidelines.)",
                            "sub_items": [
                                "Seating in work, waiting, or meeting areas is designed or selected to support comfortable posture in most areas (more than half of relevant spaces) (e.g., chairs with back support, appropriate seat height and depth)",
                                "Circulation and layout allow sufficient space for comfortable movement and safe use of furniture and equipment in most areas (more than half of relevant spaces)",
                                "Furniture design accommodates a range of users and body sizes, including the provision of adjustable or ergonomically designed elements in most areas (more than half of relevant spaces) (e.g., varied seating types, adjustable workstations)",
                            ],
                        }],
                    },
                ],
            },
        ],
    },
    # =========================================================
    # CATEGORY B — SAFETY AND CARE
    # =========================================================
    {
        "id": "B",
        "name": "Safety and Care",
        "attributes": [
            {
                "id": "1", "name": "Hygiene and Maintenance",
                "indicators": [
                    {
                        "id": "1.1", "name": "Waste storage room",
                        "questions": [
                            {"qid": "B_Q1", "type": TYPE_SCREENING_NA,
                             "text": "Does the building provide a dedicated waste storage room handling odor- or pollutant-generating waste?"},
                            {"qid": "B_Q2", "type": TYPE_MULTI,
                             "text": "What are the characteristics of the waste storage room?",
                             "sub_items": [
                                 "Waste storage room handling odor or pollutant generating waste have a separate ventilation system (separate; direct exhaust to the exterior)",
                                 "Waste storage areas are located near the sources of waste that require controlled handling (for example, sanitary waste, food waste, and clinical or infectious waste)",
                             ]},
                        ],
                    },
                    {
                        "id": "1.2", "name": "Cleaning storage",
                        "questions": [
                            {"qid": "B_Q3", "type": TYPE_SCREENING,
                             "text": "Does the building provide a dedicated storage room for the cleaning products and equipment?"},
                            {"qid": "B_Q4", "type": TYPE_MULTI,
                             "text": "What are the characteristics of the dedicated cleaning supplies storage room?",
                             "sub_items": [
                                 "Dedicated storage rooms or areas for cleaning products are distributed to ensure access without requiring unnecessary travel within or between floors (e.g., located on each floor or positioned to minimize travel distances)",
                                 "The dedicated storage room(s) is closed and has a separated ventilation system (separate and direct exhaust to the exterior)",
                             ]},
                        ],
                    },
                    {
                        "id": "1.3", "name": "Changing room for cleaning staff",
                        "questions": [
                            {"qid": "B_Q5", "type": TYPE_SCREENING,
                             "text": "Does the building provide an appropriate changing area that can be used by cleaning staff (e.g., dedicated or shared with other staff)?"},
                            {"qid": "B_Q6", "type": TYPE_MULTI,
                             "text": "What are the characteristics of the dedicated changing area for the cleaning staff?",
                             "sub_items": [
                                 "The changing area includes lockers for storing personal belongings",
                                 "The changing area includes seating to support changing comfortably",
                             ]},
                        ],
                    },
                    {
                        "id": "1.4", "name": "Healthy interior materials",
                        "questions": [{
                            "qid": "B_Q7", "type": TYPE_MULTI,
                            "text": "Are interior finishes and materials applied to most (more than half) of the main interior surfaces (e.g., floors, walls, ceilings, counters, partitions) specified or selected based on their contribution to occupant health? (Recognized healthy-materials resources: Friendly Materials, Habitable, GBCE materials platform.)",
                            "sub_items": [
                                "The main interior horizontal and vertical surfaces (e.g., floors, walls, worktops) are finished with continuous, non-porous materials that prevent dirt accumulation, are resistant to frequent cleaning and disinfectant products",
                                "Finishes and materials used in main interior surfaces have low emissions of volatile organic compounds (e.g., low-VOC or certified low-emission products)",
                            ],
                        }],
                    },
                    {
                        "id": "1.5", "name": "HVAC and maintenance",
                        "questions": [
                            {"qid": "B_Q8", "type": TYPE_SCREENING,
                             "text": "Does the building have a HVAC system (heating and/or air-conditioning equipment used to control indoor temperature) serving the main occupied areas?"},
                            {"qid": "B_Q9", "type": TYPE_YESNO_IDK,
                             "text": "Are HVAC maintenance requirements defined and/or implemented (e.g., in project documentation or maintenance plans), including regular inspection, filter replacement, and cleaning?"},
                        ],
                    },
                    {
                        "id": "1.6", "name": "Hot water Legionella prevention",
                        "questions": [
                            {"qid": "B_Q10", "type": TYPE_SCREENING,
                             "text": "Does the building have a centralized hot-water system (e.g., a boiler, heat pump, or storage tank distributing hot water through the building) that supplies sinks, showers, or kitchens? (Local electric heaters serving only one sink or appliance do not count as a centralized hot-water system.)"},
                            {"qid": "B_Q11", "type": TYPE_MULTI,
                             "text": "Which of the following Legionella prevention measures are in place for the hot-water system (according to Spanish regulations or technical guidance)? (For project-stage buildings, refer to design specifications or intended operation. Regulation reference: RD 487/2022 and RD 614/2024.)",
                             "sub_items": [
                                 "Hot water systems are designed to enable the maintenance of temperatures that reduce Legionella risk (e.g., centralized vs decentralized systems, storage tanks sized correctly, minimizing long pipe runs, thermostatic controls, recirculation loops)",
                                 "The hot water system is designed to allow regular flushing and disinfection, especially for infrequently used outlets (e.g., minimizing dead legs, providing accessible drain or flushing points, designing recirculation loops, or ensuring easy access to valves and outlets for maintenance)",
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "2", "name": "Prevention & Awareness",
                "indicators": [
                    {
                        "id": "2.1", "name": "Emergency resources",
                        "questions": [{
                            "qid": "B_Q12", "type": TYPE_MULTI,
                            "text": "Which of the following emergency resources (elements/equipment) is available in the building or its design to ensure safety in case of an emergency? The question considers good practices that enhance safety, beyond minimum code requirements.",
                            "sub_items": [
                                "ABC Powder Extinguishers and/or fire hoses (on each floor along main circulation routes and near exits, ≤15 m travel distance, clearly visible and unobstructed)",
                                "Fire alarm system (manual call points near exits and stair doors on each floor, with audible/visual alarms covering all occupied areas)",
                                "Emergency Lighting (along evacuation routes in corridors, stairs and exits, activating automatically during power failure)",
                                "Emergency Signage (green for exits/first aid, red for fire; placed at decision points, along escape routes and at each emergency device)",
                                "Automated External Defibrillators (AEDs) are adequately provided in accessible, visible, and clearly signposted locations, available to staff and visitors",
                            ],
                        }],
                    },
                    {
                        "id": "2.2", "name": "Health-promoting signs",
                        "questions": [
                            {"qid": "B_Q13", "type": TYPE_SCREENING,
                             "text": "Does the building design or project include an allocated budget for health-promoting signage, such as tobacco-free zones, motivational signage for stair use, hand washing, and physical activity?"},
                            {"qid": "B_Q14", "type": TYPE_MULTI,
                             "text": "Which of the following health-promoting signage is easily visible and appropriately placed within the building design? For project-stage buildings, answers may be based on design documentation (e.g., drawings, signage plans, or specifications).",
                             "sub_items": [
                                 "No-smoking / tobacco-free zones (visible and permanent signs at all main outdoor areas, such as building entrances and immediate surroundings, indicating that smoking is not allowed in these spaces)",
                                 "Motivational message for stair use (permanent signs at most (more than half) of the decision points such as elevator waiting areas or/and at the stair entrances)",
                                 "Hand washing signs (permanent signs in all the bathrooms and if available in all food areas)",
                                 "Other permanent signage encouraging healthy habits in communal areas (such as healthy eating and physical activity)",
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "3", "name": "Safety & Security",
                "indicators": [
                    {
                        "id": "3.1", "name": "Exterior visibility",
                        "questions": [{
                            "qid": "B_Q15", "type": TYPE_GRADED,
                            "text": "Are building entrances, exits, and their immediate surroundings provided with adequate and evenly distributed exterior lighting to support visibility and safety during dark hours? Please choose one that applies.",
                            "options": [
                                {"label": "Yes (all main building entrances and exits, including those from outdoor or indoor parking, are provided with exterior lighting that ensures even illumination and minimizes dark or shadowed areas).", "score": 1.0},
                                {"label": "Some areas lack evenly distributed lighting (one or more entrances, exits, or approach paths have insufficient illumination, or rely primarily on lighting from interior spaces).", "score": 0.5},
                                {"label": "No (many entrances and surrounding areas lack adequate and evenly distributed exterior lighting, resulting in poorly illuminated areas).", "score": 0.0},
                            ],
                        }],
                    },
                    {
                        "id": "3.2", "name": "Safety during maintenance",
                        "questions": [{
                            "qid": "B_Q16", "type": TYPE_MULTI,
                            "text": "Do building designs allow maintenance activities (cleaning, repairs, servicing) to be carried out safely without exposing building users to hazards?",
                            "sub_items": [
                                "The building design allows maintenance activities to be carried out in areas that can be separated from occupied spaces (e.g., dedicated service rooms, accessible technical shafts, ceiling systems, or isolatable zones)",
                                "The building design incorporates hazard warnings (clearly visible warning signs for slips, trips and falls, electrical or chemical hazards, and other risks, placed at all exact locations where the hazard may occur, using standardized safety pictograms)",
                            ],
                        }],
                    },
                    {
                        "id": "3.3", "name": "Emergency gathering point",
                        "questions": [{
                            "qid": "B_Q17", "type": TYPE_YESNO_NA,
                            "text": "Is there a designated emergency gathering point clearly identified and signposted for the building (e.g., on displayed evacuation maps and signage)? "
                                    "(N/A for very small buildings with direct street exit only. Regulation reference: Real Decreto 393/2007 / CTE DB-SI.)",
                        }],
                    },
                    {
                        "id": "3.4", "name": "Emergency exit signs",
                        "questions": [{
                            "qid": "B_Q18", "type": TYPE_YESNO,
                            "text": "Are all doors used as emergency exits (including any designated emergency exits) designed to be clearly signed, unobstructed, and usable during occupancy? (Regulation reference: Real Decreto 393/2007 / CTE DB-SI.)",
                        }],
                    },
                    {
                        "id": "3.5", "name": "Visibility and spatial safety",
                        "questions": [{
                            "qid": "B_Q19", "type": TYPE_MULTI,
                            "text": "Are circulation routes, common areas, and key facilities (e.g., restrooms) designed to support users' safety, with good visibility and minimal unsafe blind spots, supporting natural surveillance throughout all the related areas?",
                            "sub_items": [
                                "Circulation routes and common areas are designed to provide uniform lighting that avoids dark areas, shadows, and visual obstructions along paths of movement",
                                "Spaces are designed with clear sightlines and visual connections between circulation routes and adjacent areas, reducing blind spots and hidden corners",
                                "Restrooms are located near common areas, visible from main circulation routes, and do not create secluded corridors or hidden corners",
                            ],
                        }],
                    },
                    {
                        "id": "3.6", "name": "Contact reduction",
                        "questions": [{
                            "qid": "B_Q20", "type": TYPE_GRADED,
                            "text": "Do interaction points (e.g., security checkpoints, reception areas, checkout counters) include spatial or physical measures that help reduce close-contact exposure between individuals (e.g., barriers, increased spacing, or layout separation)? Choose one that applies.",
                            "options": [
                                {"label": "Yes, interaction areas include design elements such as barriers, spacing, or layout features that reduce close contact.", "score": 1.0},
                                {"label": "Some, measures are present in some areas but not consistently across interaction points.", "score": 0.5},
                                {"label": "No, interaction areas lack design elements such as barriers or spacing, requiring close proximity between people.", "score": 0.0},
                            ],
                        }],
                    },
                ],
            },
        ],
    },
    # =========================================================
    # CATEGORY C — SOCIAL SUPPORT
    # =========================================================
    {
        "id": "C",
        "name": "Social Support",
        "attributes": [
            {
                "id": "1", "name": "Visual / Auditory Privacy and Mental Restoration",
                "indicators": [
                    {
                        "id": "1.1", "name": "Quiet work areas",
                        "questions": [
                            {"qid": "C_Q1", "type": TYPE_SCREENING_NA,
                             "text": "Does the building provide a dedicated quiet workspace or room for staff to do concentrated work? (N/A if there is no staff at the facility, or there are no regularly occupied spaces where occupants remain for extended periods.)"},
                            {"qid": "C_Q2", "type": TYPE_MULTI,
                             "text": "What are the characteristics of the dedicated quiet workspace area/room?",
                             "sub_items": [
                                 "The area is physically separated from collaborative zones or public service areas (e.g., by walls, partitions, or being located in a different wing)",
                                 "The room or area has material acoustic treatment for sound reduction (absorbent finishes, doors, partitions)",
                                 "There are workstations that provide both visual and auditory isolation (e.g., soundproof booths)",
                                 "There are visual cues/signage indicating quiet rules",
                                 "There are privacy booths (phone booths) within or close to workspaces",
                             ]},
                        ],
                    },
                    {
                        "id": "1.2", "name": "Private room",
                        "questions": [
                            {"qid": "C_Q3", "type": TYPE_SCREENING_NA,
                             "text": "Does the building provide a private room that accommodates diverse personal needs of the staff (e.g., breastfeeding, prayer, meditation)? (N/A if there is no long-term staff at the facility, or there are no regularly occupied spaces where occupants remain for extended periods.)"},
                            {"qid": "C_Q4", "type": TYPE_GRADED,
                             "text": "What are the characteristics of the private room? Choose the one that applies.",
                             "options": [
                                 {"label": "Fully Equipped: a lockable room is available with seating, an electrical socket, a sink, and a refrigerator available within close proximity.", "score": 1.0},
                                 {"label": "Basic: a lockable room is available, but it lacks other dedicated amenities.", "score": 0.5},
                                 {"label": "Not adequate: a room exists but does not meet basic usability or comfort requirements.", "score": 0.0},
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "2", "name": "Recreation & Interaction",
                "indicators": [
                    {
                        "id": "2.1", "name": "Multi-Purpose Space",
                        "questions": [{
                            "qid": "C_Q5", "type": TYPE_YESNO_NA,
                            "text": "Does the building provide dedicated multi-purpose space(s) for staff well-being activities (e.g., physical, educational, and/or recreational activities)? (N/A if there is no staff at the facility, or there are no regularly occupied spaces where occupants remain for extended periods.)",
                        }],
                    },
                    {
                        "id": "2.2", "name": "Communal area(s)",
                        "questions": [
                            {"qid": "C_Q6", "type": TYPE_YESNO_NA,
                             "text": "Does the building provide at least one communal area or shared space per floor (such as a lounge, meeting area) where staff can interact outside of workstations? (N/A if there is no staff at the facility, or there are no regularly occupied spaces where occupants remain for extended periods.)"},
                            {"qid": "C_Q7", "type": TYPE_YESNO_NA,
                             "text": "Does the building provide a dedicated break room (a shared space for meal preparation and coffee breaks) for staff, equipped with seating and eating amenities (e.g., a kitchenette or pantry)? (N/A if there is no staff at the facility, or there are no regularly occupied spaces where occupants remain for extended periods.)"},
                        ],
                    },
                ],
            },
            {
                "id": "3", "name": "Community Needs",
                "indicators": [
                    {
                        "id": "3.1", "name": "Publicly accessible toilets",
                        "questions": [
                            {"qid": "C_Q8", "type": TYPE_SCREENING_NA,
                             "text": "Does the building provide restrooms at or near the entrance or lobby area that are available to the general public, including individuals who do not require the building's services? (N/A if the building has no spatial opportunity for general public access.)"},
                            {"qid": "C_Q9", "type": TYPE_MULTI,
                             "text": "What are the characteristics of the public-access restroom?",
                             "sub_items": [
                                 "Restroom(s) is fully adapted for people with reduced mobility (following local regulations/CTE)",
                                 "Restrooms are clearly visible or signposted from the entrance or lobby area and can be accessed without passing through restricted zones",
                                 "Restrooms provide inclusive options (e.g., universal or single-user facilities, changing tables accessible to all genders)",
                             ]},
                        ],
                    },
                    {
                        "id": "3.2", "name": "Publicly accessible climate refuge",
                        "questions": [{
                            "qid": "C_Q10", "type": TYPE_YESNO_NA,
                            "text": "Does the building provide a ground-floor 'Climate Refuge' that is open to the general public and equipped with all essential supplies (e.g., shade, permanent seating, water supply, etc.)? (N/A if the building has no spatial opportunity for general public access. Reference: Llei 16/2017 del canvi clim\u00e0tic and ESCACC30 guidelines.)",
                        }],
                    },
                ],
            },
        ],
    },
    # =========================================================
    # CATEGORY D — MENTAL & EMOTIONAL WELLBEING
    # =========================================================
    {
        "id": "D",
        "name": "Mental & Emotional Wellbeing",
        "attributes": [
            {
                "id": "1", "name": "Art & Aesthetics",
                "indicators": [
                    {
                        "id": "1.1", "name": "Art integration opportunities",
                        "questions": [{
                            "qid": "D_Q1", "type": TYPE_MULTI,
                            "text": "Does the building design support opportunities for integrating art (e.g., permanent or rotating art installations) into interior or exterior spaces? (Reference: Llei del percentatge cultural de Catalunya (Llei 8/2021), Llei 2/2023, del 14 de febrer, del sistema de l\u2019habitatge, l\u2019arquitectura i l\u2019urbanisme de Catalunya.)",
                            "sub_items": [
                                "Walls, surfaces, or architectural elements (e.g., mounting points, display systems) are available and suitable for displaying or integrating artwork",
                                "Circulation or common areas include spaces where art could be installed without obstructing movement or function",
                                "Lighting conditions (natural or artificial) can support the visibility or highlighting of art",
                                "Outdoor or transitional areas (entrances, courtyards, facades) provide opportunities for artistic integration",
                            ],
                        }],
                    },
                    {
                        "id": "1.2", "name": "Architectural aesthetics",
                        "questions": [{
                            "qid": "D_Q2", "type": TYPE_MULTI,
                            "text": "Does the building design create a visually coherent environment in most (more than half) of its main areas through its materials, forms, colors, and spatial composition, including elements that reflect or incorporate natural qualities?",
                            "sub_items": [
                                "Design elements incorporate natural or nature-referenced materials and finishes (e.g., wood, stone, natural textures, or patterns inspired by natural forms)",
                                "Material use follows a consistent strategy across spaces, without abrupt or uncoordinated variations in most main areas (e.g., consistent materials across different areas or zones)",
                                "The design incorporates materials, finishes, and building elements that are durable and easy to maintain, supporting good condition over time in most main areas",
                            ],
                        }],
                    },
                    {
                        "id": "1.3", "name": "Color use and visual environment",
                        "questions": [{
                            "qid": "D_Q3", "type": TYPE_MULTI,
                            "text": "How does the building design use color to support visual comfort, orientation, and appropriate levels of stimulation in regularly occupied areas? (For design-stage projects, responses may be based on documented color strategies, e.g., palettes, drawings, specifications, and where relevant, visualizations or simulation outputs.)",
                            "sub_items": [
                                "A defined color strategy is applied consistently across spaces based on explicit criteria related to well-being, emotional comfort, or health (e.g., documented palette, repeated color logic, or consistent material/color schemes across similar space types)",
                                "Color use varies according to space function (e.g., calmer tones in rest or waiting areas, more active or contrasting colors in circulation or activity areas)",
                                "Color contrast, intensity, and saturation are used to avoid excessive visual strain (e.g., no harsh contrasts, glare-prone finishes, or overly saturated environments in most areas)",
                                "Colour is used to support spatial readability, orientation, and hierarchy (for example, distinguishing uses, routes, or marking transition areas)",
                            ],
                        }],
                    },
                ],
            },
            {
                "id": "2", "name": "Views",
                "indicators": [
                    {
                        "id": "2.1", "name": "Outdoor nature views",
                        "questions": [
                            {"qid": "D_Q4", "type": TYPE_SCREENING_NA,
                             "text": "Does the building design enable access to outdoor views of natural elements from regularly occupied spaces?"},
                            {"qid": "D_Q5", "type": TYPE_MULTI,
                             "text": "Outdoor nature view characteristics:",
                             "sub_items": [
                                 "All or majority of regularly occupied areas have direct views of outdoor natural elements",
                                 "Nature views available from majority of seating / workstation locations (≥50–75%)",
                             ]},
                        ],
                    },
                    {
                        "id": "2.2", "name": "Indoor nature elements",
                        "questions": [
                            {"qid": "D_Q6", "type": TYPE_SCREENING_NA,
                             "text": "Does the building include indoor natural elements (plants, green walls, water features) in regularly occupied spaces?"},
                            {"qid": "D_Q7", "type": TYPE_MULTI,
                             "text": "Indoor nature view characteristics:",
                             "sub_items": [
                                 "Majority of regularly occupied spaces include visible indoor natural elements",
                                 "Interior layouts designed so indoor nature is visible from majority of seating locations",
                                 "Larger nature-integrated spaces (indoor gardens, courtyards, atria) included",
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "3", "name": "Outdoors / Nature",
                "indicators": [
                    {
                        "id": "3.1", "name": "Basic nature access",
                        "questions": [{
                            "qid": "D_Q8", "type": TYPE_YESNO_NA,
                            "text": "Does the building design provide access to at least one outdoor space with vegetation or natural elements (on-site or within a 5–6 minute walking distance)? Applicable to buildings with continuous use or where occupants spend extended periods of time (e.g., work, study, waiting, or rest). (N/A if the building is primarily used for short-duration or event-based activities with no staff.)",
                        }],
                    },
                    {
                        "id": "3.2", "name": "Outdoor space – Restorative qualities",
                        "questions": [{
                            "qid": "D_Q9", "type": TYPE_MULTI,
                            "text": "How does the outdoor space support restorative use for building users? Indicate whether the following conditions are met.",
                            "sub_items": [
                                "The outdoor space incorporates natural elements (e.g., vegetation, trees, gardens, water features)",
                                "The outdoor space incorporates seating and shade for rest",
                                "The outdoor space is protected or buffered from heavy traffic, noise, or surrounding building disturbances (e.g., through landscaping, setbacks, enclosure, or location)",
                            ],
                        }],
                    },
                    {
                        "id": "3.3", "name": "Outdoor space for recreation or physical activity",
                        "questions": [{
                            "qid": "D_Q10", "type": TYPE_YESNO_NA,
                            "text": "Does the building design enable access to outdoor spaces that are meant to support physical activity or sport (e.g., walking paths, exercise areas, playgrounds, sports courts)? Applicable to buildings with continuous use or areas where occupants spend extended periods of time (e.g., work, study, waiting, or rest). (N/A if the building is primarily used for short-duration or event-based activities with no staff.)",
                        }],
                    },
                ],
            },
            {
                "id": "4", "name": "Daylight",
                "indicators": [
                    {
                        "id": "4.1", "name": "Daylight access",
                        "questions": [
                            {"qid": "D_Q11", "type": TYPE_YESNO,
                             "text": "Does the building design provide daylight access in most (more than half) of the regularly occupied areas (e.g., staff work areas, break rooms, lounges, waiting or seating areas)?"},
                            {"qid": "D_Q12", "type": TYPE_MULTI,
                             "text": "Which of the following characteristics describes how the building design provides daylight access in regularly occupied areas (e.g., staff work areas, break rooms, lounges, waiting or seating areas)?",
                             "sub_items": [
                                 "Most (more than half) regularly occupied areas (e.g., staff work areas, lounges, waiting or seating areas) receive natural daylight through windows, skylights, or similar openings",
                                 "Daylight distribution reaches more than half of the workstations or seating if available (observed on site or demonstrated through daylight simulation/analysis for design-stage projects)",
                                 "Daylight provides sufficient and evenly distributed illumination without causing excessive glare, supported by appropriate glazing or shading strategies (e.g., window treatments, solar control glazing, external shading)",
                                 "Electric lighting is designed to support circadian rhythms, particularly in areas with limited or no daylight (e.g., variation in light intensity and/or color temperature throughout the day)",
                             ]},
                        ],
                    },
                ],
            },
        ],
    },
    # =========================================================
    # CATEGORY E — COMFORT AND QUALITY
    # =========================================================
    {
        "id": "E",
        "name": "Comfort and Quality",
        "attributes": [
            {
                "id": "1", "name": "Acoustics",
                "indicators": [
                    {
                        "id": "1.1", "name": "Exterior Acoustic Comfort",
                        "questions": [
                            {"qid": "E_Q1", "type": TYPE_YESNO_IDK,
                             "text": "Does the building comply with applicable national or local regulations for protection against external noise (CTE DB-HR in Spain), including the acoustic insulation requirements corresponding to the building's environmental noise classification? (Applicable regulation: CTE DB-HR / Local noise maps or acoustic zoning.)"},
                            {"qid": "E_Q2", "type": TYPE_MULTI,
                             "text": "How does the building design reduce exposure to exterior noise in regularly occupied areas? Indicate whether the following conditions are met in most (more than half) of applicable spaces.",
                             "sub_items": [
                                 "The building envelope (e.g., fa\u00e7ade, windows, doors) includes acoustic insulation measures designed to reduce external noise intrusion into regularly occupied spaces",
                                 "Buffer zones or spatial strategies (e.g., entrance lobbies, corridors, intermediate spaces, setbacks from noise sources or surrounding vegetation) help reduce exposure to outdoor noise",
                             ]},
                        ],
                    },
                    {
                        "id": "1.2", "name": "Interior Acoustic Comfort",
                        "questions": [
                            {"qid": "E_Q3", "type": TYPE_YESNO_IDK,
                             "text": "Does the building comply with applicable national or local regulations for interior acoustic performance (e.g., CTE DB-HR in Spain)? (CTE DB-HR establishes requirements for airborne sound insulation between spaces, impact noise between floors, noise from building installations, and acoustic comfort in interior spaces, based on acoustic design calculations, simulations, or certified measurements, depending on the project stage.)"},
                            {"qid": "E_Q4", "type": TYPE_MULTI,
                             "text": "How does the building design support acoustic comfort inside regularly occupied areas? Indicate whether the following conditions are met in most (more than half) of applicable spaces.",
                             "sub_items": [
                                 "Interior finishes or materials include sound-absorbing elements (e.g., acoustic ceilings, wall panels, soft finishes) to reduce reverberation and noise",
                                 "Doors, partitions, or construction details include acoustic sealing or insulation to limit sound transmission between spaces",
                                 "Measures are implemented to reduce impact noise (e.g., footsteps, furniture movement) where relevant (e.g., floor finishes, structural isolation)",
                                 "Building services and equipment (e.g., HVAC, plumbing, mechanical systems) include acoustic insulation or vibration control to minimize noise",
                             ]},
                        ],
                    },
                    {
                        "id": "1.3", "name": "Acoustic zones",
                        "questions": [{
                            "qid": "E_Q5", "type": TYPE_MULTI,
                            "text": "How are different activity areas acoustically separated or organized in the building? Indicate whether the following conditions are met in most (more than half) of applicable spaces.",
                            "sub_items": [
                                "Spatial layout (zoning) separates quiet and noisy areas, including the use of distance and/or transitional buffer spaces (e.g., quiet areas located away from noise sources, corridors or service spaces placed between quiet and active zones)",
                                "Sound transfer between areas with different noise levels is provided through sound-insulating elements (e.g., walls, doors, or partitions designed to limit sound transmission)",
                            ],
                        }],
                    },
                ],
            },
            {
                "id": "2", "name": "Lighting",
                "indicators": [
                    {
                        "id": "2.1", "name": "Lighting conditions",
                        "questions": [{
                            "qid": "E_Q6", "type": TYPE_MULTI,
                            "text": "Lighting conditions in regularly occupied areas:",
                            "sub_items": [
                                "Workstation / task areas have sufficient and even lighting (≥500 lux)",
                                "Communal / circulation areas have sufficient lighting (≥200–300 lux)",
                                "Lighting evenly distributed across spaces",
                                "Lighting design minimizes glare",
                                "Good color rendering (CRI ≥80, appropriate color temperature)",
                                "Lighting systems avoid visible flicker",
                                "Lighting supports circadian rhythms (where relevant)",
                            ],
                        }],
                    },
                ],
            },
            {
                "id": "3", "name": "Indoor Climate",
                "indicators": [
                    {
                        "id": "3.1", "name": "Thermal comfort compliance",
                        "questions": [{
                            "qid": "E_Q7", "type": TYPE_YESNO_IDK,
                            "text": "Does the building's thermal comfort design (through mechanical systems, passive strategies, or hybrid solutions) comply with applicable national or local regulations (e.g., RITE in Spain)? (RITE: Reglamento de Instalaciones Térmicas en los Edificios. Compliance may be demonstrated through building design documentation, system specifications, or operational performance. Additional voluntary guidance: ASHRAE 55, WELL Building Standard – Thermal Comfort.)",
                        }],
                    },
                    {
                        "id": "3.2", "name": "Temperature",
                        "questions": [{
                            "qid": "E_Q8", "type": TYPE_MULTI,
                            "text": "How are indoor temperature conditions managed in regularly occupied areas? Indicate whether the following conditions are met in most (more than half) of applicable spaces.",
                            "sub_items": [
                                "Building systems or passive strategies (e.g., HVAC or hybrid systems, shading devices, thermal mass, or insulation strategies) are designed to maintain indoor temperatures within recommended comfort ranges (e.g., ~20–26 °C depending on season)",
                                "Temperature conditions can be regulated or moderated in different areas of the building (e.g., HVAC zoning, shading systems, or other thermal control strategies)",
                                "Thermal design responds to solar exposure or façade orientation (e.g., shading devices, glazing strategies, façade treatments, or layout adjustments)",
                                "Areas with high occupancy or high heat gain (e.g., meeting rooms, waiting areas, auditoriums) have dedicated or adjustable temperature control",
                            ],
                        }],
                    },
                    {
                        "id": "3.3", "name": "Air velocity / Air movement",
                        "questions": [{
                            "qid": "E_Q9", "type": TYPE_MULTI,
                            "text": "How is air movement managed to maintain thermal comfort in regularly occupied areas? Indicate whether the following conditions are met in most (more than half) of applicable spaces. (Relevant guidance: ASHRAE 55 – Thermal Environmental Conditions for Human Occupancy; EN 16798-1 – Indoor environmental input parameters for building design.)",
                            "sub_items": [
                                "Ventilation and airflow distribution are designed to provide balanced air movement without causing drafts or direct airflow on occupants (e.g., appropriate diffuser placement, displacement ventilation, or supply air positioned away from seating/work areas)",
                                "Air movement can be adjusted or moderated in different spaces (e.g., operable windows, ventilation controls, ceiling fans, or zoned mechanical ventilation), without disrupting the operation of mechanical systems where applicable",
                            ],
                        }],
                    },
                    {
                        "id": "3.4", "name": "Humidity",
                        "questions": [{
                            "qid": "E_Q10", "type": TYPE_MULTI,
                            "text": "How is indoor humidity managed in the building? Indicate whether the following conditions are met in most (more than half) of applicable spaces. (Relevant references: RITE; ASHRAE 55; EN 16798-1. Common standards recommend maintaining relative humidity between approximately 30% and 60% in regularly occupied spaces.)",
                            "sub_items": [
                                "Building systems are designed (e.g., HVAC humidity control, ventilation design, or design calculations/simulations) to maintain indoor humidity within recommended ranges (typically ~30–60% RH)",
                                "Ventilation systems, building systems (e.g., HVAC), or passive strategies include humidity control or moisture management strategies where relevant (e.g., exhaust fans in bathrooms/kitchens, mechanical ventilation, or natural ventilation strategies)",
                                "Building envelope and ventilation design reduce risks of condensation or moisture accumulation (e.g., insulated façades/windows, vapor barriers, or adequate ventilation in humid areas)",
                            ],
                        }],
                    },
                ],
            },
            {
                "id": "4", "name": "Air Quality",
                "indicators": [
                    {
                        "id": "4.1", "name": "Smoke-free signage / smoke-free perimeter",
                        "questions": [{
                            "qid": "E_Q11", "type": TYPE_MULTI,
                            "text": "How does the building maintain a smoke-free environment? Indicate whether the following conditions are met.",
                            "sub_items": [
                                "Clear smoke-free signage is present at building entrances and near outdoor areas clearly stating that outdoor smoking is restricted near entrances, windows, or ventilation intakes",
                                "The building site or immediate surroundings include a defined smoke-free perimeter",
                            ],
                        }],
                    },
                    {
                        "id": "4.2", "name": "Entryway systems / Outdoor pollutant prevention",
                        "questions": [{
                            "qid": "E_Q12", "type": TYPE_MULTI,
                            "text": "How does the building design limit outdoor pollutants entering indoor spaces? Indicate whether the following conditions are met in most (more than half) of applicable spaces. (Entryway systems prevent outdoor pollutants from entering.)",
                            "sub_items": [
                                "Main entrances include entryway systems that capture dirt and pollutants, extending approximately 3 m (or the maximum available length) in the direction of travel and covering the full width of the entrance path (e.g., walk-off mats or equivalent systems)",
                                "Entrances are designed to reduce direct airflow from outdoors into occupied spaces (e.g., vestibules, air curtains, or double-door entry layouts)",
                            ],
                        }],
                    },
                    {
                        "id": "4.3", "name": "Asbestos Safety",
                        "questions": [{
                            "qid": "E_Q13", "type": TYPE_GRADED,
                            "text": "Which statement best describes how asbestos risks affecting indoor air quality are addressed in the building? Choose one that applies.",
                            "options": [
                                {"label": "Yes, the building was constructed after the ban on asbestos-containing materials in Spain (2002) and no asbestos-containing materials are known or documented; or the building was constructed before the ban and a professional assessment has confirmed the absence of asbestos materials (remediation has been implemented by qualified professionals).", "score": 1.0},
                                {"label": "No, the building was constructed before the ban and asbestos assessment has not been conducted, and the presence of asbestos-containing materials is unknown.", "score": 0.0},
                                {"label": "I don't know, documentation/information not available.", "score": None},
                            ],
                        }],
                    },
                    {
                        "id": "4.4", "name": "Source separation",
                        "questions": [{
                            "qid": "E_Q14", "type": TYPE_MULTI,
                            "text": "How are internal pollutant or odor sources separated from regularly occupied areas in the building? Indicate whether the following conditions are met in most (more than half) of the applicable spaces.",
                            "sub_items": [
                                "Spaces with pollutant or odor sources (e.g., bathrooms, kitchens, storage rooms) have separate or dedicated exhaust ventilation",
                                "Spaces with pollutant or odor sources are physically separated or buffered from regularly occupied spaces",
                                "Ventilation systems prevent air from pollutant or odor-generating spaces being transferred or recirculated into regularly occupied areas (e.g., direct exhaust to outdoors, no return air mixing from these spaces)",
                            ],
                        }],
                    },
                    {
                        "id": "4.5", "name": "Ventilation Strategies / Outdoor air supply",
                        "questions": [{
                            "qid": "E_Q15", "type": TYPE_MULTI,
                            "text": "How does the building design ensure adequate fresh air supply and outdoor pollutant removal? Indicate whether the following conditions are met in most (more than half) of the applicable spaces, where relevant.",
                            "sub_items": [
                                "The building provides adequate outdoor air supply through mechanical, natural, or hybrid ventilation strategies, designed in accordance with applicable regulations (e.g., RITE or equivalent)",
                                "Ventilation strategies are designed to support continuous air renewal in regularly occupied areas (e.g., through mechanical supply systems, operable windows, or cross-ventilation)",
                                "Ventilation strategies are designed and integrated into the building layout to avoid negative impacts on thermal comfort, humidity conditions, or energy performance (e.g., controlled mechanical ventilation, heat recovery systems, cross-ventilation design, automated window controls, or integration with shading and thermal design)",
                                "Outdoor air intakes and ventilation openings are located and designed to minimize the entry of outdoor pollutants into the building (e.g., positioned away from traffic or exhaust sources, appropriate separation between intake and exhaust)",
                            ],
                        }],
                    },
                    {
                        "id": "4.6", "name": "Compliance with Indoor Air Quality Regulations",
                        "questions": [{
                            "qid": "E_Q16", "type": TYPE_YESNO_IDK,
                            "text": "Are the building's indoor air quality conditions designed to comply with applicable regulations or standards (e.g., RITE in Spain, EN/ASHRAE/WELL guidelines)?",
                        }],
                    },
                    {
                        "id": "4.7", "name": "Indoor Air Quality Management / Monitoring",
                        "questions": [{
                            "qid": "E_Q17", "type": TYPE_MULTI,
                            "text": "How does the building design support the monitoring and control of indoor air quality conditions? (Indoor air quality may be assessed according to RITE, WHO Indoor Air Quality Guidelines, ASHRAE 62.1, or EN 16798-1. Monitoring commonly includes CO\u2082, particulate matter, VOCs, temperature, and humidity.)",
                            "sub_items": [
                                "Design includes indoor air quality monitoring systems or sensors (e.g., CO\u2082, particulate matter, VOCs, temperature, humidity) accessible to building managers and/or shared with occupants",
                                "The building includes design strategies to limit indoor pollutant sources (e.g., ventilation design, filtration, low-emission materials)",
                                "Ventilation and filtration systems that are included in the building design allow proper maintenance and filter replacement in accordance with manufacturer or regulatory requirements",
                            ],
                        }],
                    },
                    {
                        "id": "4.8", "name": "Indoor Vegetation",
                        "questions": [
                            {"qid": "E_Q18", "type": TYPE_SCREENING,
                             "text": "Does the building design intentionally incorporate indoor vegetation (e.g., planted areas, green walls, interior planters integrated into the design)? Indoor vegetation refers to plants intentionally integrated into interior spaces (e.g., clusters of plants, planted areas, green walls, or planters forming part of the spatial design), rather than isolated decorative plants."},
                            {"qid": "E_Q19", "type": TYPE_MULTI,
                             "text": "How does the building design support the integration and maintenance of indoor vegetation in the most (more than half) relevant areas?",
                             "sub_items": [
                                 "Vegetation, plant selection and placement consider indoor environmental conditions (e.g., lighting availability, proximity to windows or skylights, airflow patterns, humidity levels, and compatibility of plant species with indoor conditions)",
                                 "Irrigation or planting systems avoid excessive indoor humidity or moisture accumulation (e.g., controlled irrigation systems, drip irrigation instead of open watering, adequate drainage in planters, waterproof planting beds, moisture barriers, or ventilation provided around indoor gardens)",
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "5", "name": "Potable Water",
                "indicators": [
                    {
                        "id": "5.1", "name": "Access to Potable Drinking Water",
                        "questions": [{
                            "qid": "E_Q20", "type": TYPE_MULTI,
                            "text": "How does the building design provide and make potable drinking water accessible?",
                            "sub_items": [
                                "Drinking water is available through fountains or refill stations connected to the building's potable water supply",
                                "Drinking water points are adequately distributed and located in accessible common areas or circulation spaces",
                                "Drinking water access (e.g., fountains or refill stations) is provided or planned to support the use of refillable bottles",
                            ],
                        }],
                    },
                    {
                        "id": "5.2", "name": "Lead contamination control",
                        "questions": [{
                            "qid": "E_Q21", "type": TYPE_GRADED,
                            "text": "Which statement best describes how potential lead risks from building materials or plumbing systems are addressed in building design? Choose one that applies.",
                            "options": [
                                {"label": "Plumbing systems and interior materials are designed without lead-containing components (e.g., pipes, solder, fittings, or paints).", "score": 1.0},
                                {"label": "Lead-containing materials have not been evaluated or addressed in the building design, or their presence is unknown based on available information.", "score": 0.0},
                                {"label": "I don't know (no information or documentation available to confirm material composition or assessment).", "score": None},
                            ],
                        }],
                    },
                ],
            },
            {
                "id": "6", "name": "Urban Environmental Integration",
                "indicators": [
                    {
                        "id": "6.1", "name": "Urban Heat-Island Mitigation",
                        "questions": [{
                            "qid": "E_Q22", "type": TYPE_MULTI,
                            "text": "What design strategies are used to reduce heat accumulation in the surrounding environment? Indicate whether the following conditions are met in most (more than half) of the applicable areas.",
                            "sub_items": [
                                "Roofs or terraces include cool materials, green roofs, or reflective surfaces that reduce solar heat absorption",
                                "Outdoor areas use light-colored or permeable surfaces that help moderate local temperatures",
                                "Outdoor areas include vegetation or tree cover that helps reduce local heat buildup",
                            ],
                        }],
                    },
                    {
                        "id": "6.2", "name": "Urban landscape integration",
                        "questions": [
                            {"qid": "E_Q23", "type": TYPE_MULTI,
                             "text": "How does the building design integrate with the surrounding urban environment?",
                             "sub_items": [
                                 "Building façades at ground level maintain visual connection with surrounding streets and outdoor public areas through transparency, entrances, or active frontages, avoiding long blank or inactive façade sections",
                                 "Ground-level areas include publicly accessible uses or spaces (e.g., seating areas, public art, or climate-responsive spaces such as heat shelters) that encourage social interaction",
                             ]},
                        ],
                    },
                    {
                        "id": "6.3", "name": "Outdoor thermal conditions",
                        "questions": [
                            {"qid": "E_Q24", "type": TYPE_SCREENING,
                             "text": "Does the building include outdoor spaces under its control (e.g., courtyard, terrace, garden, roof terrace, or entrance forecourt)?"},
                            {"qid": "E_Q25", "type": TYPE_MULTI,
                             "text": "How does the building design support comfortable outdoor conditions in its external spaces? Indicate whether the following conditions are met in most (more than half) of the applicable spaces.",
                             "sub_items": [
                                 "Outdoor spaces include shade from trees, canopies, or architectural elements",
                                 "Outdoor seating or waiting areas are protected from excessive sun exposure or heat buildup",
                                 "Surface materials (e.g., light-coloured finishes, permeable pavements, or low heat-retaining materials) are used to reduce heat accumulation and improve outdoor thermal comfort",
                             ]},
                        ],
                    },
                ],
            },
        ],
    },
]


# ============================================================
# Skip-logic visibility rules
# Maps a question id to a (controller_qid, required_value) pair.
# If the controller is not equal to required_value, the question is hidden.
# ============================================================
VISIBILITY_RULES = {
    # Category A
    "A_Q7":  ("A_Q6",  "Yes"),
    "A_Q13": ("A_Q12", "Yes"),
    "A_Q15": ("A_Q14", "Yes"),
    "A_Q19": ("A_Q18", "Yes"),
    "A_Q22": ("A_Q21", "Yes"),
    # Category B
    "B_Q2":  ("B_Q1",  "Yes"),
    "B_Q4":  ("B_Q3",  "Yes"),
    "B_Q6":  ("B_Q5",  "Yes"),
    "B_Q9":  ("B_Q8",  "Yes"),
    "B_Q11": ("B_Q10", "Yes"),
    "B_Q14": ("B_Q13", "Yes"),
    # Category C
    "C_Q2":  ("C_Q1",  "Yes"),
    "C_Q4":  ("C_Q3",  "Yes"),
    "C_Q9":  ("C_Q8",  "Yes"),
    # Category D
    "D_Q5":  ("D_Q4",  "Yes"),
    "D_Q7":  ("D_Q6",  "Yes"),
    "D_Q9":  ("D_Q8",  "Yes"),
    # Category E
    "E_Q19": ("E_Q18", "Yes"),
    "E_Q25": ("E_Q24", "Yes"),
}


# ============================================================
# Scoring helpers
# ============================================================
def get(qid):
    return st.session_state.get(qid)


def get_sub(qid, idx):
    return st.session_state.get(f"{qid}_{idx}")


def yn_score(ans):
    if ans == "Yes":
        return 1.0
    if ans == "No":
        return 0.0
    return None


def graded_score_for(question, ans):
    if ans is None:
        return None
    for opt in question["options"]:
        if opt["label"] == ans:
            return opt["score"]
    return None


def question_value_score(question):
    """Score a single question (used inside indicator scorers)."""
    qid = question["qid"]
    qtype = question["type"]
    ans = get(qid)
    if qtype == TYPE_YESNO:
        return yn_score(ans)
    if qtype == TYPE_YESNO_IDK:
        if ans in (None, "I don't know"):
            return None
        return yn_score(ans)
    if qtype == TYPE_YESNO_NA:
        if ans in (None, "N/A"):
            return None
        return yn_score(ans)
    if qtype == TYPE_GRADED:
        return graded_score_for(question, ans)
    if qtype == TYPE_MULTI:
        return multi_question_score(question)
    return None


def multi_question_score(question):
    vals = []
    for i, _ in enumerate(question["sub_items"]):
        s = yn_score(get_sub(question["qid"], i))
        if s is not None:
            vals.append(s)
    if not vals:
        return None
    return sum(vals) / len(vals)


def multi_subitem_values(qid, n):
    vals = []
    for i in range(n):
        s = yn_score(get_sub(qid, i))
        if s is not None:
            vals.append(s)
    return vals


def find_question(category, ind_id, qid):
    for attr in category["attributes"]:
        for ind in attr["indicators"]:
            if ind["id"] == ind_id:
                for q in ind["questions"]:
                    if q["qid"] == qid:
                        return q
    return None


# ----- screening helpers -----
def screen_then_value(screen_qid, follow_question, na_excludes):
    """Screening question controls a follow-up question.
       Returns the indicator score (0-1) or None if excluded."""
    s = get(screen_qid)
    if s is None:
        return None
    if s == "N/A":
        return None if na_excludes else 0.0
    if s == "No":
        return 0.0
    if s == "Yes":
        return question_value_score(follow_question)
    return None


# ============================================================
# Special-case indicator scorers
# Keyed by (category_id, indicator_id) → callable returning score in [0,1] or None
# ============================================================
def _A_1_6():
    cat = CATEGORIES_BY_ID["A"]
    return screen_then_value("A_Q6", find_question(cat, "1.6", "A_Q7"), na_excludes=False)

def _A_3_3():
    cat = CATEGORIES_BY_ID["A"]
    return screen_then_value("A_Q12", find_question(cat, "3.3", "A_Q13"), na_excludes=False)

def _A_3_4():
    cat = CATEGORIES_BY_ID["A"]
    return screen_then_value("A_Q14", find_question(cat, "3.4", "A_Q15"), na_excludes=False)

def _A_5_1():
    cat = CATEGORIES_BY_ID["A"]
    return screen_then_value("A_Q18", find_question(cat, "5.1", "A_Q19"), na_excludes=False)

def _A_6_2():
    cat = CATEGORIES_BY_ID["A"]
    return screen_then_value("A_Q21", find_question(cat, "6.2", "A_Q22"), na_excludes=True)

def _B_1_1():
    cat = CATEGORIES_BY_ID["B"]
    return screen_then_value("B_Q1", find_question(cat, "1.1", "B_Q2"), na_excludes=True)

def _B_1_2():
    cat = CATEGORIES_BY_ID["B"]
    return screen_then_value("B_Q3", find_question(cat, "1.2", "B_Q4"), na_excludes=False)

def _B_1_3():
    cat = CATEGORIES_BY_ID["B"]
    return screen_then_value("B_Q5", find_question(cat, "1.3", "B_Q6"), na_excludes=False)

def _B_1_5():
    cat = CATEGORIES_BY_ID["B"]
    return screen_then_value("B_Q8", find_question(cat, "1.5", "B_Q9"), na_excludes=False)

def _B_1_6():
    cat = CATEGORIES_BY_ID["B"]
    return screen_then_value("B_Q10", find_question(cat, "1.6", "B_Q11"), na_excludes=False)

def _B_2_2():
    cat = CATEGORIES_BY_ID["B"]
    return screen_then_value("B_Q13", find_question(cat, "2.2", "B_Q14"), na_excludes=False)

def _C_1_1():
    cat = CATEGORIES_BY_ID["C"]
    return screen_then_value("C_Q1", find_question(cat, "1.1", "C_Q2"), na_excludes=True)

def _C_1_2():
    cat = CATEGORIES_BY_ID["C"]
    return screen_then_value("C_Q3", find_question(cat, "1.2", "C_Q4"), na_excludes=True)

def _C_2_2():
    # Average of Q6 and Q7 (both yesno_na). N/A excluded; unanswered excluded.
    vals = []
    for qid in ("C_Q6", "C_Q7"):
        s = get(qid)
        if s in ("Yes", "No"):
            vals.append(yn_score(s))
    if not vals:
        return None
    return sum(vals) / len(vals)

def _C_3_1():
    cat = CATEGORIES_BY_ID["C"]
    return screen_then_value("C_Q8", find_question(cat, "3.1", "C_Q9"), na_excludes=True)

def _D_2_1():
    cat = CATEGORIES_BY_ID["D"]
    return screen_then_value("D_Q4", find_question(cat, "2.1", "D_Q5"), na_excludes=True)

def _D_2_2():
    cat = CATEGORIES_BY_ID["D"]
    return screen_then_value("D_Q6", find_question(cat, "2.2", "D_Q7"), na_excludes=True)

def _D_3_2():
    # Q9 multi only counts if Q8 == Yes. Q8=No → 0; Q8=N/A or unanswered → excluded.
    s = get("D_Q8")
    if s in (None, "N/A"):
        return None
    if s == "No":
        return 0.0
    return multi_question_score(find_question(CATEGORIES_BY_ID["D"], "3.2", "D_Q9"))

def _D_4_1():
    # Pool Q11 (yesno) and Q12 (multi 4-item) sub-items into a single average.
    vals = []
    s = yn_score(get("D_Q11"))
    if s is not None:
        vals.append(s)
    vals.extend(multi_subitem_values("D_Q12", 4))
    if not vals:
        return None
    return sum(vals) / len(vals)

def _E_1_1():
    # Pool Q1 (yesno_idk; idk excluded) and Q2 multi (2 items).
    vals = []
    ans = get("E_Q1")
    if ans in ("Yes", "No"):
        vals.append(yn_score(ans))
    vals.extend(multi_subitem_values("E_Q2", 2))
    if not vals:
        return None
    return sum(vals) / len(vals)

def _E_1_2():
    vals = []
    ans = get("E_Q3")
    if ans in ("Yes", "No"):
        vals.append(yn_score(ans))
    vals.extend(multi_subitem_values("E_Q4", 4))
    if not vals:
        return None
    return sum(vals) / len(vals)

def _E_4_8():
    cat = CATEGORIES_BY_ID["E"]
    return screen_then_value("E_Q18", find_question(cat, "4.8", "E_Q19"), na_excludes=False)

def _E_6_2():
    # Q23 (multi 2) always contributes; Q25 (multi 3) only if Q24=Yes.
    vals = list(multi_subitem_values("E_Q23", 2))
    if get("E_Q24") == "Yes":
        vals.extend(multi_subitem_values("E_Q25", 3))
    if not vals:
        return None
    return sum(vals) / len(vals)


SPECIAL_INDICATORS = {
    ("A", "1.6"): _A_1_6,
    ("A", "3.3"): _A_3_3,
    ("A", "3.4"): _A_3_4,
    ("A", "5.1"): _A_5_1,
    ("A", "6.2"): _A_6_2,
    ("B", "1.1"): _B_1_1,
    ("B", "1.2"): _B_1_2,
    ("B", "1.3"): _B_1_3,
    ("B", "1.5"): _B_1_5,
    ("B", "1.6"): _B_1_6,
    ("B", "2.2"): _B_2_2,
    ("C", "1.1"): _C_1_1,
    ("C", "1.2"): _C_1_2,
    ("C", "2.2"): _C_2_2,
    ("C", "3.1"): _C_3_1,
    ("D", "2.1"): _D_2_1,
    ("D", "2.2"): _D_2_2,
    ("D", "3.2"): _D_3_2,
    ("D", "4.1"): _D_4_1,
    ("E", "1.1"): _E_1_1,
    ("E", "1.2"): _E_1_2,
    ("E", "4.8"): _E_4_8,
    ("E", "6.2"): _E_6_2,
}


CATEGORIES_BY_ID = {c["id"]: c for c in CATEGORIES}


def indicator_score(category, ind):
    key = (category["id"], ind["id"])
    if key in SPECIAL_INDICATORS:
        return SPECIAL_INDICATORS[key]()
    # Default: indicator has a single question, score it directly.
    if len(ind["questions"]) == 1:
        return question_value_score(ind["questions"][0])
    # Fallback for any unspecified multi-question indicator: average questions.
    vals = [question_value_score(q) for q in ind["questions"]]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)


def attribute_score(category, attr):
    vals = [indicator_score(category, i) for i in attr["indicators"]]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)


def category_score(category):
    vals = [attribute_score(category, a) for a in category["attributes"]]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)


# ============================================================
# UI rendering
# ============================================================
def question_visible(qid):
    rule = VISIBILITY_RULES.get(qid)
    if rule is None:
        return True
    ctrl_qid, required = rule
    return get(ctrl_qid) == required


def display_qid(qid):
    return qid.split("_", 1)[1]


def is_question_answered(q):
    """Return True if all parts of a visible question have been answered."""
    qid = q["qid"]
    qtype = q["type"]
    if qtype == TYPE_MULTI:
        for i in range(len(q["sub_items"])):
            if st.session_state.get(f"{qid}_{i}") is None:
                return False
        return True
    else:
        return st.session_state.get(qid) is not None


def get_unanswered_questions(category):
    """Return list of display IDs for unanswered visible questions in a category."""
    unanswered = []
    for attr in category["attributes"]:
        for ind in attr["indicators"]:
            for q in ind["questions"]:
                if question_visible(q["qid"]) and not is_question_answered(q):
                    unanswered.append(display_qid(q["qid"]))
    return unanswered


def render_question(q):
    qid = q["qid"]
    qtype = q["type"]
    label = f"**{display_qid(qid)}.** {q['text']}"

    if qtype == TYPE_MULTI:
        st.markdown(label)
        for i, item in enumerate(q["sub_items"]):
            st.radio(item, ["Yes", "No"], key=f"{qid}_{i}", index=None, horizontal=True)
    elif qtype == TYPE_YESNO:
        st.radio(label, ["Yes", "No"], key=qid, index=None, horizontal=True)
    elif qtype == TYPE_YESNO_IDK:
        st.radio(label, ["Yes", "No", "I don't know"], key=qid, index=None, horizontal=True)
    elif qtype == TYPE_YESNO_NA:
        st.radio(label, ["Yes", "No", "N/A"], key=qid, index=None, horizontal=True)
    elif qtype == TYPE_SCREENING:
        st.radio(label, ["Yes", "No"], key=qid, index=None, horizontal=True)
    elif qtype == TYPE_SCREENING_NA:
        st.radio(label, ["Yes", "No", "N/A"], key=qid, index=None, horizontal=True)
    elif qtype == TYPE_GRADED:
        labels = [opt["label"] for opt in q["options"]]
        st.radio(label, labels, key=qid, index=None)


def render_category(category):
    st.header(f"Category {category['id']}: {category['name']}")
    for attr in category["attributes"]:
        st.subheader(f"Attribute {attr['id']}: {attr['name']}")
        for ind in attr["indicators"]:
            with st.container(border=True):
                st.markdown(f"#### Indicator {ind['id']} — {ind['name']}")
                for q in ind["questions"]:
                    if question_visible(q["qid"]):
                        render_question(q)
                    else:
                        st.caption(
                            f"_{display_qid(q['qid'])} skipped based on a previous "
                            f"answer (scoring follows the skip rule)._"
                        )
    # Show warning for unanswered questions in this category
    unanswered = get_unanswered_questions(category)
    if unanswered:
        st.warning(
            f"⚠️ {len(unanswered)} unanswered question(s) in this category: "
            f"{', '.join(unanswered)}. All questions must be answered."
        )


def render_results():
    st.header("📊 Results")

    # Overall scores per category
    cat_scores = []
    for cat in CATEGORIES:
        s = category_score(cat)
        cat_scores.append((cat, s))

    valid_scores = [s for _, s in cat_scores if s is not None]
    overall = sum(valid_scores) / len(valid_scores) if valid_scores else None

    top_left, top_right = st.columns([1, 2])

    with top_left:
        if overall is None:
            st.metric("Overall (mean of categories)", "—")
        else:
            score_pct = overall * 100
            st.metric("Overall (mean of categories)", f"{score_pct:.1f} / 100")
            # Score interpretation
            if score_pct >= 90:
                lbl, color, meaning, action = "Excellent", "green", "Exceptional, exceeds best practice", "Celebrate & share as model"
            elif score_pct >= 70:
                lbl, color, meaning, action = "Good", "olive", "Solid, meets healthy building goals", "Sustain; minor tweaks"
            elif score_pct >= 50:
                lbl, color, meaning, action = "Satisfactory", "orange", "Basic adequacy, noticeable gaps possible", "Targeted improvements"
            elif score_pct >= 25:
                lbl, color, meaning, action = "Poor", "red", "Significant deficits, occupant health at risk", "Priority intervention"
            else:
                lbl, color, meaning, action = "Critical", "darkred", "Critical failure, immediate action needed", "Red alert / retrofit"
            st.markdown(
                f"**Rating:** :{color}[{lbl}]  \n"
                f"**Meaning:** {meaning}  \n"
                f"**Action:** {action}"
            )

        # Count "I don't know" answers
        idk_count = 0
        for key, val in st.session_state.items():
            if key.startswith(("A_", "B_", "C_", "D_", "E_")) and val == "I don't know":
                idk_count += 1
        if idk_count > 0:
            st.info(
                f"ℹ️ **\"I don't know\" answers: {idk_count}**  \n"
                f"Indicates an information/documentation gap: Excluded from the "
                f"calculation, not treated as bad performance."
            )

        st.subheader("Category scores")
        for cat, s in cat_scores:
            label = f"{cat['id']}. {cat['name']}"
            if s is None:
                st.write(f"**{label}** — _excluded (no valid data)_")
            else:
                st.write(f"**{label}** — {s * 100:.1f} / 100")
                st.progress(s)

    with top_right:
        labels = [c["name"] for c in CATEGORIES]
        scores = [0.0 if s is None else s * 100 for _, s in cat_scores]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],
            theta=labels + [labels[0]],
            fill="toself",
            name="Categories",
            line=dict(color="#2E7D32"),
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            title="Category scores (0–100)",
            height=520,
            margin=dict(t=60, b=40, l=40, r=40),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Excluded categories are plotted as 0; see the list on the left "
            "for which categories are actually excluded from scoring."
        )

    st.divider()

    # Per-category detail: spider chart of attributes + hierarchical table
    for cat, cat_s in cat_scores:
        st.subheader(f"Category {cat['id']}: {cat['name']} — {('excluded' if cat_s is None else f'{cat_s * 100:.1f} / 100')}")

        # Attribute spider chart for this category
        attr_labels = [f"{a['id']}. {a['name']}" for a in cat["attributes"]]
        attr_scores_list = []
        for attr in cat["attributes"]:
            s = attribute_score(cat, attr)
            attr_scores_list.append(0.0 if s is None else s * 100)

        chart_col, table_col = st.columns([1, 1])

        with chart_col:
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=attr_scores_list + [attr_scores_list[0]],
                theta=attr_labels + [attr_labels[0]],
                fill="toself",
                name="Attributes",
                line=dict(color="#1565C0"),
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                title=f"Attribute scores — Category {cat['id']}",
                height=420,
                margin=dict(t=60, b=40, l=80, r=80),
            )
            st.plotly_chart(fig, use_container_width=True)

        with table_col:
            # Hierarchical table: Attribute > Indicator with scores
            rows = []
            for attr in cat["attributes"]:
                a_s = attribute_score(cat, attr)
                rows.append({
                    "Level": "Attribute",
                    "Name": f"{attr['id']}. {attr['name']}",
                    "Score (0–100)": "excluded" if a_s is None else f"{a_s * 100:.1f}",
                })
                for ind in attr["indicators"]:
                    i_s = indicator_score(cat, ind)
                    rows.append({
                        "Level": "  Indicator",
                        "Name": f"  {ind['id']} — {ind['name']}",
                        "Score (0–100)": "excluded" if i_s is None else f"{i_s * 100:.1f}",
                    })
            st.dataframe(rows, use_container_width=True, hide_index=True)

        st.divider()


# ============================================================
# App layout
# ============================================================
st.title("Health-Promoting Spaces Scoring Tool")
st.caption(
    "MVP. Use the sidebar to navigate categories. Skipped questions, N/A and "
    "\"I don't know\" answers are excluded from scoring per the official rules."
)

with st.sidebar:
    st.markdown("### Navigation")
    nav_options = [f"{c['id']}. {c['name']}" for c in CATEGORIES] + ["📊 Results"]
    selection = st.radio("Section", nav_options, label_visibility="collapsed")

    st.divider()
    st.markdown("### Category scores")
    for cat in CATEGORIES:
        missing = get_unanswered_questions(cat)
        if missing:
            st.write(f"**{cat['id']}.** {cat['name']} — _incomplete_")
        else:
            s = category_score(cat)
            if s is None:
                st.write(f"**{cat['id']}.** {cat['name']} — _excluded_")
            else:
                st.write(f"**{cat['id']}.** {cat['name']} — {s * 100:.0f}")

    st.divider()
    if st.button("Reset all answers", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith(("A_", "B_", "C_", "D_", "E_")):
                del st.session_state[key]
        st.rerun()

# Main pane
if selection == "📊 Results":
    # Check all categories for unanswered questions
    all_unanswered = {}
    for cat in CATEGORIES:
        missing = get_unanswered_questions(cat)
        if missing:
            all_unanswered[f"{cat['id']}. {cat['name']}"] = missing
    if all_unanswered:
        st.error("❌ All questions must be answered before viewing results.")
        for cat_name, questions in all_unanswered.items():
            st.warning(f"**{cat_name}** — unanswered: {', '.join(questions)}")
    else:
        render_results()
else:
    cat_id = selection.split(".", 1)[0].strip()
    # Enforce sequential completion: previous categories must be complete
    cat_index = next(i for i, c in enumerate(CATEGORIES) if c["id"] == cat_id)
    blocked_by = []
    for prev_cat in CATEGORIES[:cat_index]:
        if get_unanswered_questions(prev_cat):
            blocked_by.append(f"{prev_cat['id']}. {prev_cat['name']}")
    if blocked_by:
        st.warning(
            f"🔒 Please complete the following categories first: "
            f"{', '.join(blocked_by)}"
        )
    else:
        render_category(CATEGORIES_BY_ID[cat_id])
