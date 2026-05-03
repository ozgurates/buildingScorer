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
                        "id": "1.1", "name": "Proximity to daily services",
                        "questions": [{
                            "qid": "A_Q1", "type": TYPE_MULTI,
                            "text": "Are the following daily services accessible within ~5–6 min walking distance?",
                            "sub_items": [
                                "Public transit stops",
                                "Food access point",
                                "Financial service",
                                "Healthcare provider",
                                "Care or education facility",
                                "Essential goods and services retail",
                            ],
                        }],
                    },
                    {
                        "id": "1.2", "name": "Recreational amenities",
                        "questions": [{
                            "qid": "A_Q2", "type": TYPE_MULTI,
                            "text": "Are the following physical activity / recreational amenities accessible within ~5–6 min walking distance?",
                            "sub_items": [
                                "Public outdoor green space",
                                "Sports and physical activity facilities",
                            ],
                        }],
                    },
                    {
                        "id": "1.3", "name": "Pedestrian safety measures",
                        "questions": [{
                            "qid": "A_Q3", "type": TYPE_MULTI,
                            "text": "Are any of the following pedestrian safety measures implemented near the building?",
                            "sub_items": [
                                "Lower speed limits (≤30 km/h) in more than half of street segments within ~400 m",
                                "Pedestrian priority measures at more than half of nearby intersections within ~400 m",
                                "Continuous physical buffers along pedestrian / bicycle routes",
                            ],
                        }],
                    },
                    {
                        "id": "1.4", "name": "Safe arrival design",
                        "questions": [{
                            "qid": "A_Q4", "type": TYPE_MULTI,
                            "text": "How does the building support safe and accessible arrival?",
                            "sub_items": [
                                "Safe drop-off or pick-up areas provided",
                                "Pedestrian access routes are safe and accessible",
                                "Arrival areas minimize conflicts between pedestrians, cyclists and vehicles",
                            ],
                        }],
                    },
                    {
                        "id": "1.5", "name": "Bicycle / micromobility parking",
                        "questions": [{
                            "qid": "A_Q5", "type": TYPE_YESNO,
                            "text": "Is there convenient parking for bicycles and micromobility devices near the main entrance (~30 m)?",
                        }],
                    },
                    {
                        "id": "1.6", "name": "Bicycle network connectivity",
                        "questions": [
                            {"qid": "A_Q6", "type": TYPE_SCREENING,
                             "text": "Are there bicycle routes within proximity of the main building entrance?"},
                            {"qid": "A_Q7", "type": TYPE_GRADED,
                             "text": "What are the characteristics of the bicycle routes?",
                             "options": [
                                 {"label": "All elements present (separate, accessible, uninterrupted)", "score": 1.0},
                                 {"label": "Some elements present (partial separation, occasional interruptions)", "score": 0.5},
                                 {"label": "None of the required elements present", "score": 0.0},
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "2", "name": "Intersectionality",
                "indicators": [
                    {
                        "id": "2.1", "name": "Accessibility code compliance",
                        "questions": [{
                            "qid": "A_Q8", "type": TYPE_YESNO_IDK,
                            "text": "Does the building comply with the Catalan Accessibility Code (Decree 209/2023)?",
                        }],
                    },
                    {
                        "id": "2.2", "name": "Inclusive restrooms",
                        "questions": [{
                            "qid": "A_Q9", "type": TYPE_MULTI,
                            "text": "Does the building support inclusive and safe use of restroom facilities?",
                            "sub_items": [
                                "Provides male, female AND universal single-user restroom",
                                "Restroom signage clearly indicates available options",
                                "Changing tables accessible to all users",
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
                            "text": "Are wayfinding signs available in key locations and main circulation areas?",
                        }],
                    },
                    {
                        "id": "3.2", "name": "Spatial legibility",
                        "questions": [{
                            "qid": "A_Q11", "type": TYPE_MULTI,
                            "text": "Spatial legibility of the building:",
                            "sub_items": [
                                "Space is easy to understand from entry (clear sightlines)",
                                "Use of color codes or differentiated materials",
                                "Graphic landmarks at decision points",
                            ],
                        }],
                    },
                    {
                        "id": "3.3", "name": "Internal services directory",
                        "questions": [
                            {"qid": "A_Q12", "type": TYPE_SCREENING,
                             "text": "Does the building include a permanent internal services directory at the main entrance?"},
                            {"qid": "A_Q13", "type": TYPE_MULTI,
                             "text": "Characteristics of the internal services directory:",
                             "sub_items": [
                                 "Completeness of internal information",
                                 "Clear information with internal navigation",
                                 "Easy to read (high-contrast, legible font)",
                                 "Accessible to diverse users (braille / audio)",
                             ]},
                        ],
                    },
                    {
                        "id": "3.4", "name": "Nearby services directory",
                        "questions": [
                            {"qid": "A_Q14", "type": TYPE_SCREENING,
                             "text": "Does the building include a permanent nearby services directory at the main entrance?"},
                            {"qid": "A_Q15", "type": TYPE_MULTI,
                             "text": "Characteristics of the nearby services directory:",
                             "sub_items": [
                                 "Shows nearby facilities (transit, food, banks) updated regularly",
                                 "Shows nearby public outdoor spaces",
                                 "Uses high-contrast colors and clear font",
                                 "Includes graphic signage, braille and / or audio",
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "4", "name": "Technology & Digitalization",
                "indicators": [
                    {
                        "id": "4.1", "name": "Connectivity quality",
                        "questions": [{
                            "qid": "A_Q16", "type": TYPE_GRADED,
                            "text": "Digital connectivity in the building:",
                            "options": [
                                {"label": "Optimized connectivity (ALARA-aligned)", "score": 1.0},
                                {"label": "Standard full Wi-Fi coverage (no ALARA)", "score": 0.5},
                                {"label": "Partial or no connectivity", "score": 0.0},
                            ],
                        }],
                    },
                    {
                        "id": "4.2", "name": "Technological features",
                        "questions": [{
                            "qid": "A_Q17", "type": TYPE_YESNO,
                            "text": "Does the building include at least one technological feature for usability?",
                        }],
                    },
                ],
            },
            {
                "id": "5", "name": "Environmental Control",
                "indicators": [
                    {
                        "id": "5.1", "name": "Personal environmental control",
                        "questions": [
                            {"qid": "A_Q18", "type": TYPE_SCREENING,
                             "text": "Does the facility include regularly occupied staff or work areas?"},
                            {"qid": "A_Q19", "type": TYPE_MULTI,
                             "text": "Indoor environmental controls for staff:",
                             "sub_items": [
                                 "Individual task lighting",
                                 "Operable shading",
                                 "Personal temperature control",
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "6", "name": "Physical Activity Promotion",
                "indicators": [
                    {
                        "id": "6.1", "name": "On-site activity infrastructure",
                        "questions": [{
                            "qid": "A_Q20", "type": TYPE_MULTI,
                            "text": "Facilities for promoting physical activity:",
                            "sub_items": [
                                "Bicycle racks inside the building (staff)",
                                "Fitness area within building or 5–6 min walk",
                                "Showers and lockers within the building",
                            ],
                        }],
                    },
                    {
                        "id": "6.2", "name": "Active stair use",
                        "questions": [
                            {"qid": "A_Q21", "type": TYPE_SCREENING_NA,
                             "text": "Does the building include a stair connecting publicly accessible floors?"},
                            {"qid": "A_Q22", "type": TYPE_MULTI,
                             "text": "Stair design strategies:",
                             "sub_items": [
                                 "Basic access (connects all publicly accessible floors)",
                                 "Full building access (connects all floors top to bottom)",
                                 "Prominent location (near elevators or main lobby)",
                                 "Safety enhancements (contrasting treads, handrails)",
                                 "Aesthetics (art, color, lighting, music)",
                                 "Stair-use encouraging signs at most decision points",
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "7", "name": "Ergonomics",
                "indicators": [
                    {
                        "id": "7.1", "name": "Ergonomic design",
                        "questions": [{
                            "qid": "A_Q23", "type": TYPE_MULTI,
                            "text": "Ergonomic design of regularly occupied spaces:",
                            "sub_items": [
                                "Seating supports comfortable posture in most areas",
                                "Circulation / layout allows comfortable movement in most areas",
                                "Furniture accommodates a range of users in most areas",
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
                             "text": "Does the building provide a dedicated waste storage room for odor / pollutant-generating waste?"},
                            {"qid": "B_Q2", "type": TYPE_MULTI,
                             "text": "Waste storage room characteristics:",
                             "sub_items": [
                                 "Separate ventilation system (direct exhaust to exterior)",
                                 "Located near sources of waste that require controlled handling",
                             ]},
                        ],
                    },
                    {
                        "id": "1.2", "name": "Cleaning supplies storage",
                        "questions": [
                            {"qid": "B_Q3", "type": TYPE_SCREENING,
                             "text": "Does the building provide a dedicated storage room for cleaning products and equipment?"},
                            {"qid": "B_Q4", "type": TYPE_MULTI,
                             "text": "Cleaning storage room characteristics:",
                             "sub_items": [
                                 "Distributed to ensure access without unnecessary travel",
                                 "Closed and has a separated ventilation system",
                             ]},
                        ],
                    },
                    {
                        "id": "1.3", "name": "Cleaning staff facilities",
                        "questions": [
                            {"qid": "B_Q5", "type": TYPE_SCREENING,
                             "text": "Does the building provide an appropriate changing area for cleaning staff?"},
                            {"qid": "B_Q6", "type": TYPE_MULTI,
                             "text": "Changing area characteristics:",
                             "sub_items": [
                                 "Includes lockers for storing personal belongings",
                                 "Includes seating to support comfortable changing",
                             ]},
                        ],
                    },
                    {
                        "id": "1.4", "name": "Surface materials",
                        "questions": [{
                            "qid": "B_Q7", "type": TYPE_MULTI,
                            "text": "Interior finishes and materials on most main surfaces:",
                            "sub_items": [
                                "Continuous, non-porous materials (resistant to cleaning / disinfection)",
                                "Low emissions of VOCs (low-VOC or certified products)",
                            ],
                        }],
                    },
                    {
                        "id": "1.5", "name": "HVAC maintenance",
                        "questions": [
                            {"qid": "B_Q8", "type": TYPE_SCREENING,
                             "text": "Does the building have an HVAC system serving main occupied areas?"},
                            {"qid": "B_Q9", "type": TYPE_YESNO_IDK,
                             "text": "Are HVAC maintenance requirements defined and / or implemented?"},
                        ],
                    },
                    {
                        "id": "1.6", "name": "Legionella prevention",
                        "questions": [
                            {"qid": "B_Q10", "type": TYPE_SCREENING,
                             "text": "Does the building have a centralized hot-water system?"},
                            {"qid": "B_Q11", "type": TYPE_MULTI,
                             "text": "Legionella prevention measures:",
                             "sub_items": [
                                 "Hot water system designed to maintain temperatures that reduce Legionella risk",
                                 "Designed to allow regular flushing and disinfection",
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
                            "text": "Emergency resources available in the building:",
                            "sub_items": [
                                "ABC Powder extinguishers and / or fire hoses",
                                "Fire alarm system",
                                "Emergency lighting",
                                "Emergency signage",
                                "AEDs in accessible, visible locations",
                            ],
                        }],
                    },
                    {
                        "id": "2.2", "name": "Health-promoting signage",
                        "questions": [
                            {"qid": "B_Q13", "type": TYPE_SCREENING,
                             "text": "Does the building design include an allocated budget for health-promoting signage?"},
                            {"qid": "B_Q14", "type": TYPE_MULTI,
                             "text": "Health-promoting signage present:",
                             "sub_items": [
                                 "No-smoking / tobacco-free zone signs at all main outdoor areas",
                                 "Motivational stair-use messages at most decision points",
                                 "Hand washing signs in all bathrooms and food areas",
                                 "Other permanent signage encouraging healthy habits",
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "3", "name": "Safety & Security",
                "indicators": [
                    {
                        "id": "3.1", "name": "Exterior lighting",
                        "questions": [{
                            "qid": "B_Q15", "type": TYPE_GRADED,
                            "text": "Exterior lighting at building entrances and surroundings:",
                            "options": [
                                {"label": "Yes — all main entrances / exits with even illumination", "score": 1.0},
                                {"label": "Some — one or more lacking even illumination", "score": 0.5},
                                {"label": "No — many lack adequate lighting", "score": 0.0},
                            ],
                        }],
                    },
                    {
                        "id": "3.2", "name": "Maintenance safety",
                        "questions": [{
                            "qid": "B_Q16", "type": TYPE_MULTI,
                            "text": "Safety during maintenance:",
                            "sub_items": [
                                "Building design allows maintenance in areas separable from occupied spaces",
                                "Hazard warnings clearly visible at all hazard locations",
                            ],
                        }],
                    },
                    {
                        "id": "3.3", "name": "Emergency gathering point",
                        "questions": [{
                            "qid": "B_Q17", "type": TYPE_YESNO_NA,
                            "text": "Is there a designated emergency gathering point clearly identified and signposted? "
                                    "(N/A for very small buildings with direct street exit only.)",
                        }],
                    },
                    {
                        "id": "3.4", "name": "Emergency exits",
                        "questions": [{
                            "qid": "B_Q18", "type": TYPE_YESNO,
                            "text": "Are all doors used as emergency exits clearly signed, unobstructed and usable?",
                        }],
                    },
                    {
                        "id": "3.5", "name": "Visibility and spatial safety",
                        "questions": [{
                            "qid": "B_Q19", "type": TYPE_MULTI,
                            "text": "Visibility and spatial safety:",
                            "sub_items": [
                                "Circulation routes have uniform lighting avoiding dark areas",
                                "Clear sightlines and visual connections reducing blind spots",
                                "Restrooms located near common areas, not in secluded corridors",
                            ],
                        }],
                    },
                    {
                        "id": "3.6", "name": "Contact reduction",
                        "questions": [{
                            "qid": "B_Q20", "type": TYPE_GRADED,
                            "text": "Contact reduction at interaction points:",
                            "options": [
                                {"label": "Yes — barriers, spacing or layout features present", "score": 1.0},
                                {"label": "Some — present in some but not all areas", "score": 0.5},
                                {"label": "No — lacks design elements for contact reduction", "score": 0.0},
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
                        "id": "1.1", "name": "Quiet workspace",
                        "questions": [
                            {"qid": "C_Q1", "type": TYPE_SCREENING_NA,
                             "text": "Does the building provide a dedicated quiet workspace or room for staff?"},
                            {"qid": "C_Q2", "type": TYPE_MULTI,
                             "text": "Quiet workspace characteristics:",
                             "sub_items": [
                                 "Physically separated from collaborative / public areas",
                                 "Material acoustic treatment (absorbent finishes, doors, partitions)",
                                 "Workstations with both visual and auditory isolation (soundproof booths)",
                                 "Visual cues / signage indicating quiet rules",
                                 "Privacy booths (phone booths) within or close to workspaces",
                             ]},
                        ],
                    },
                    {
                        "id": "1.2", "name": "Private personal-needs room",
                        "questions": [
                            {"qid": "C_Q3", "type": TYPE_SCREENING_NA,
                             "text": "Does the building provide a private room for diverse personal needs (breastfeeding, prayer, meditation)?"},
                            {"qid": "C_Q4", "type": TYPE_GRADED,
                             "text": "Private room characteristics:",
                             "options": [
                                 {"label": "Fully equipped (lockable, seating, socket, sink, fridge nearby)", "score": 1.0},
                                 {"label": "Basic (lockable but lacks dedicated amenities)", "score": 0.5},
                                 {"label": "Not adequate (exists but doesn't meet basic usability)", "score": 0.0},
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "2", "name": "Recreation & Interaction",
                "indicators": [
                    {
                        "id": "2.1", "name": "Multi-purpose well-being space",
                        "questions": [{
                            "qid": "C_Q5", "type": TYPE_YESNO_NA,
                            "text": "Does the building provide dedicated multi-purpose space(s) for staff well-being activities?",
                        }],
                    },
                    {
                        "id": "2.2", "name": "Communal & break areas",
                        "questions": [
                            {"qid": "C_Q6", "type": TYPE_YESNO_NA,
                             "text": "Does the building provide at least one communal area per floor for staff interaction?"},
                            {"qid": "C_Q7", "type": TYPE_YESNO_NA,
                             "text": "Does the building provide a dedicated break room for staff (kitchenette, seating)?"},
                        ],
                    },
                ],
            },
            {
                "id": "3", "name": "Community Needs",
                "indicators": [
                    {
                        "id": "3.1", "name": "Public-access restrooms",
                        "questions": [
                            {"qid": "C_Q8", "type": TYPE_SCREENING_NA,
                             "text": "Does the building provide restrooms accessible to the general public near entrance / lobby?"},
                            {"qid": "C_Q9", "type": TYPE_MULTI,
                             "text": "Public-access restroom characteristics:",
                             "sub_items": [
                                 "Fully adapted for people with reduced mobility",
                                 "Clearly visible / signposted and accessible without passing restricted zones",
                                 "Provides inclusive options (universal / single-user, changing tables)",
                             ]},
                        ],
                    },
                    {
                        "id": "3.2", "name": "Climate Refuge",
                        "questions": [{
                            "qid": "C_Q10", "type": TYPE_YESNO_NA,
                            "text": "Does the building provide a ground-floor Climate Refuge open to the general public?",
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
                        "id": "1.1", "name": "Opportunities for art",
                        "questions": [{
                            "qid": "D_Q1", "type": TYPE_MULTI,
                            "text": "Does the building design support opportunities for integrating art?",
                            "sub_items": [
                                "Walls / surfaces / architectural elements available for displaying artwork",
                                "Circulation / common areas include spaces for art installation",
                                "Lighting conditions support visibility of art",
                                "Outdoor / transitional areas provide opportunities for artistic integration",
                            ],
                        }],
                    },
                    {
                        "id": "1.2", "name": "Visual coherence",
                        "questions": [{
                            "qid": "D_Q2", "type": TYPE_MULTI,
                            "text": "Does the building design create a visually coherent environment in most main areas?",
                            "sub_items": [
                                "Natural or nature-referenced materials and finishes",
                                "Material use follows a consistent strategy across spaces",
                                "Materials / finishes are durable and easy to maintain",
                            ],
                        }],
                    },
                    {
                        "id": "1.3", "name": "Color use",
                        "questions": [{
                            "qid": "D_Q3", "type": TYPE_MULTI,
                            "text": "Color use in the building:",
                            "sub_items": [
                                "Defined color strategy applied consistently across spaces",
                                "Color varies according to space function",
                                "Color contrast / intensity avoids excessive visual strain",
                                "Color supports spatial readability and orientation",
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
                        "id": "3.1", "name": "Access to vegetated outdoor space",
                        "questions": [{
                            "qid": "D_Q8", "type": TYPE_YESNO_NA,
                            "text": "Does the building provide access to at least one outdoor space with vegetation or natural elements (on-site or within 5–6 min walk)?",
                        }],
                    },
                    {
                        "id": "3.2", "name": "Restorative outdoor space quality",
                        "questions": [{
                            "qid": "D_Q9", "type": TYPE_MULTI,
                            "text": "Restorative outdoor space quality:",
                            "sub_items": [
                                "Incorporates natural elements (vegetation, trees, water features)",
                                "Incorporates seating and shade for rest",
                                "Protected / buffered from traffic, noise or surrounding disturbances",
                            ],
                        }],
                    },
                    {
                        "id": "3.3", "name": "Outdoor activity space",
                        "questions": [{
                            "qid": "D_Q10", "type": TYPE_YESNO_NA,
                            "text": "Does the building provide access to outdoor spaces supporting physical activity or sport?",
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
                             "text": "Does the building provide daylight access in most regularly occupied areas?"},
                            {"qid": "D_Q12", "type": TYPE_MULTI,
                             "text": "Daylight access characteristics:",
                             "sub_items": [
                                 "Most regularly occupied areas receive natural daylight",
                                 "Daylight reaches more than half of workstations / seating",
                                 "Daylight provides sufficient illumination without excessive glare",
                                 "Electric lighting designed to support circadian rhythms",
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
                        "id": "1.1", "name": "Exterior noise protection",
                        "questions": [
                            {"qid": "E_Q1", "type": TYPE_YESNO_IDK,
                             "text": "Does the building comply with regulations for protection against external noise (CTE DB-HR)?"},
                            {"qid": "E_Q2", "type": TYPE_MULTI,
                             "text": "How does the building reduce exposure to exterior noise?",
                             "sub_items": [
                                 "Building envelope includes acoustic insulation measures",
                                 "Buffer zones or spatial strategies reduce exposure to outdoor noise",
                             ]},
                        ],
                    },
                    {
                        "id": "1.2", "name": "Interior acoustic comfort",
                        "questions": [
                            {"qid": "E_Q3", "type": TYPE_YESNO_IDK,
                             "text": "Does the building comply with regulations for interior acoustic performance (CTE DB-HR)?"},
                            {"qid": "E_Q4", "type": TYPE_MULTI,
                             "text": "Interior acoustic comfort:",
                             "sub_items": [
                                 "Interior finishes include sound-absorbing elements",
                                 "Doors / partitions include acoustic sealing to limit sound transmission",
                                 "Measures to reduce impact noise",
                                 "Building services include acoustic insulation or vibration control",
                             ]},
                        ],
                    },
                    {
                        "id": "1.3", "name": "Acoustic zoning",
                        "questions": [{
                            "qid": "E_Q5", "type": TYPE_MULTI,
                            "text": "Acoustic zones:",
                            "sub_items": [
                                "Spatial layout separates quiet and noisy areas",
                                "Sound transfer between areas limited through sound-insulating elements",
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
                        "id": "3.1", "name": "Thermal regulation compliance",
                        "questions": [{
                            "qid": "E_Q7", "type": TYPE_YESNO_IDK,
                            "text": "Does the building's thermal comfort design comply with RITE regulations?",
                        }],
                    },
                    {
                        "id": "3.2", "name": "Indoor temperature management",
                        "questions": [{
                            "qid": "E_Q8", "type": TYPE_MULTI,
                            "text": "Indoor temperature management:",
                            "sub_items": [
                                "Systems designed to maintain temperatures within comfort ranges (~20–26°C)",
                                "Temperature can be regulated in different areas",
                                "Thermal design responds to solar exposure / façade orientation",
                                "High-occupancy areas have dedicated / adjustable temperature control",
                            ],
                        }],
                    },
                    {
                        "id": "3.3", "name": "Air movement",
                        "questions": [{
                            "qid": "E_Q9", "type": TYPE_MULTI,
                            "text": "Air movement management:",
                            "sub_items": [
                                "Ventilation provides balanced air movement without drafts",
                                "Air movement can be adjusted in different spaces",
                            ],
                        }],
                    },
                    {
                        "id": "3.4", "name": "Indoor humidity",
                        "questions": [{
                            "qid": "E_Q10", "type": TYPE_MULTI,
                            "text": "Indoor humidity management:",
                            "sub_items": [
                                "Systems designed to maintain humidity within recommended ranges (~30–60% RH)",
                                "Ventilation / systems include humidity control or moisture management",
                                "Building envelope reduces risks of condensation or moisture accumulation",
                            ],
                        }],
                    },
                ],
            },
            {
                "id": "4", "name": "Air Quality",
                "indicators": [
                    {
                        "id": "4.1", "name": "Smoke-free environment",
                        "questions": [{
                            "qid": "E_Q11", "type": TYPE_MULTI,
                            "text": "Smoke-free environment:",
                            "sub_items": [
                                "Clear smoke-free signage at entrances and outdoor areas",
                                "Defined smoke-free perimeter on site",
                            ],
                        }],
                    },
                    {
                        "id": "4.2", "name": "Limiting outdoor pollutants entering indoors",
                        "questions": [{
                            "qid": "E_Q12", "type": TYPE_MULTI,
                            "text": "Limiting outdoor pollutants entering indoors:",
                            "sub_items": [
                                "Main entrances include entryway systems capturing dirt / pollutants (~3 m)",
                                "Entrances reduce direct airflow from outdoors (vestibules, air curtains)",
                            ],
                        }],
                    },
                    {
                        "id": "4.3", "name": "Asbestos risks",
                        "questions": [{
                            "qid": "E_Q13", "type": TYPE_GRADED,
                            "text": "Asbestos risks:",
                            "options": [
                                {"label": "Building constructed after 2002 ban OR assessed by professional with confirmed absence", "score": 1.0},
                                {"label": "Constructed before ban, assessment not conducted, presence unknown", "score": 0.0},
                                {"label": "I don't know", "score": None},
                            ],
                        }],
                    },
                    {
                        "id": "4.4", "name": "Internal pollutant separation",
                        "questions": [{
                            "qid": "E_Q14", "type": TYPE_MULTI,
                            "text": "Internal pollutant / odor source separation:",
                            "sub_items": [
                                "Spaces with pollutant sources have separate / dedicated exhaust ventilation",
                                "Spaces with pollutant sources are physically separated from occupied areas",
                                "Ventilation prevents air from pollutant spaces being recirculated into occupied areas",
                            ],
                        }],
                    },
                    {
                        "id": "4.5", "name": "Fresh air supply",
                        "questions": [{
                            "qid": "E_Q15", "type": TYPE_MULTI,
                            "text": "Fresh air supply and outdoor pollutant removal:",
                            "sub_items": [
                                "Adequate outdoor air supply through mechanical, natural or hybrid ventilation",
                                "Ventilation supports continuous air renewal in regularly occupied areas",
                                "Ventilation strategies avoid negative impacts on thermal comfort / humidity",
                                "Outdoor air intakes positioned to minimize entry of outdoor pollutants",
                            ],
                        }],
                    },
                    {
                        "id": "4.6", "name": "Indoor air quality regulations",
                        "questions": [{
                            "qid": "E_Q16", "type": TYPE_YESNO_IDK,
                            "text": "Is the building's indoor air quality designed to comply with applicable regulations?",
                        }],
                    },
                    {
                        "id": "4.7", "name": "Air quality monitoring & management",
                        "questions": [{
                            "qid": "E_Q17", "type": TYPE_MULTI,
                            "text": "Indoor air quality monitoring and management:",
                            "sub_items": [
                                "Design includes air quality monitoring systems / sensors",
                                "Design strategies to limit indoor pollutants",
                                "Ventilation / filtration systems allow proper maintenance",
                            ],
                        }],
                    },
                    {
                        "id": "4.8", "name": "Indoor vegetation",
                        "questions": [
                            {"qid": "E_Q18", "type": TYPE_SCREENING,
                             "text": "Does the building design incorporate indoor vegetation?"},
                            {"qid": "E_Q19", "type": TYPE_MULTI,
                             "text": "Indoor vegetation characteristics:",
                             "sub_items": [
                                 "Plant selection and placement consider indoor environmental conditions",
                                 "Irrigation / planting systems avoid excessive humidity or moisture accumulation",
                             ]},
                        ],
                    },
                ],
            },
            {
                "id": "5", "name": "Potable Water",
                "indicators": [
                    {
                        "id": "5.1", "name": "Drinking water access",
                        "questions": [{
                            "qid": "E_Q20", "type": TYPE_MULTI,
                            "text": "Access to potable drinking water:",
                            "sub_items": [
                                "Drinking water available through fountains or refill stations connected to potable supply",
                                "Drinking water points in accessible common areas",
                                "Drinking water access supports use of refillable bottles",
                            ],
                        }],
                    },
                    {
                        "id": "5.2", "name": "Lead contamination control",
                        "questions": [{
                            "qid": "E_Q21", "type": TYPE_GRADED,
                            "text": "Lead contamination control:",
                            "options": [
                                {"label": "Plumbing systems designed without lead-containing components", "score": 1.0},
                                {"label": "Lead-containing materials not evaluated or presence unknown", "score": 0.0},
                            ],
                        }],
                    },
                ],
            },
            {
                "id": "6", "name": "Urban Environmental Integration",
                "indicators": [
                    {
                        "id": "6.1", "name": "Heat accumulation reduction",
                        "questions": [{
                            "qid": "E_Q22", "type": TYPE_MULTI,
                            "text": "Heat accumulation reduction strategies:",
                            "sub_items": [
                                "Roofs / terraces include cool materials, green roofs or reflective surfaces",
                                "Outdoor areas use light-colored or permeable surfaces",
                                "Outdoor areas include vegetation or tree cover",
                            ],
                        }],
                    },
                    {
                        "id": "6.2", "name": "Urban landscape integration",
                        "questions": [
                            {"qid": "E_Q23", "type": TYPE_MULTI,
                             "text": "Urban landscape integration:",
                             "sub_items": [
                                 "Building façades at ground level maintain visual connection with streets",
                                 "Ground-level areas include publicly accessible uses / spaces",
                             ]},
                            {"qid": "E_Q24", "type": TYPE_SCREENING,
                             "text": "Does the building include outdoor spaces under its control (courtyard, terrace, garden)?"},
                            {"qid": "E_Q25", "type": TYPE_MULTI,
                             "text": "Comfortable outdoor conditions:",
                             "sub_items": [
                                 "Outdoor spaces include shade from trees, canopies or architectural elements",
                                 "Outdoor seating / waiting areas protected from excessive sun / heat",
                                 "Surface materials reduce heat accumulation",
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
            st.metric("Overall (mean of categories)", f"{overall * 100:.1f} / 100")

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

    # Per-attribute table
    st.subheader("Attribute scores")
    attr_rows = []
    for cat in CATEGORIES:
        for attr in cat["attributes"]:
            s = attribute_score(cat, attr)
            attr_rows.append({
                "Category": f"{cat['id']}. {cat['name']}",
                "Attribute": f"{attr['id']}. {attr['name']}",
                "Score (0–100)": "excluded" if s is None else f"{s * 100:.1f}",
            })
    st.dataframe(attr_rows, use_container_width=True, hide_index=True)

    st.divider()

    # Per-indicator table
    st.subheader("Indicator scores")
    ind_rows = []
    for cat in CATEGORIES:
        for attr in cat["attributes"]:
            for ind in attr["indicators"]:
                s = indicator_score(cat, ind)
                ind_rows.append({
                    "Category": cat["id"],
                    "Attribute": f"{attr['id']}. {attr['name']}",
                    "Indicator": f"{ind['id']} — {ind['name']}",
                    "Score (0–100)": "excluded" if s is None else f"{s * 100:.1f}",
                })
    st.dataframe(ind_rows, use_container_width=True, hide_index=True)


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
    st.markdown("### Live category scores")
    for cat in CATEGORIES:
        s = category_score(cat)
        if s is None:
            st.write(f"**{cat['id']}.** {cat['name']} — _—_")
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
    render_results()
else:
    cat_id = selection.split(".", 1)[0].strip()
    render_category(CATEGORIES_BY_ID[cat_id])
