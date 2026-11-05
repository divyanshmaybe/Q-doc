"""
Condition definitions and metadata for Q-Doc MVP.
Strict closed list: 6 common conditions + 2 special classes.
"""

from typing import Dict, Any, List

CONDITIONS = [
    "acne",
    "eczema",
    "psoriasis",
    "tinea",
    "urticaria",
    "scabies",
    "possible_malignancy",
    "other_or_unclear"
]

CONDITION_METADATA: Dict[str, Dict[str, Any]] = {
    "acne": {
        "display_name": "Acne Vulgaris",
        "hindi_name": "मुँहासे (Acne)",
        "category": "common",
        "is_special": False,
        "is_malignant": False,
        "common_sites": ["face", "chest", "upper back", "shoulders", "cheeks", "forehead"],
        "typical_symptoms": ["comedones", "papules", "pustules", "nodules", "oily skin"],
        "patient_explanation_en": "Acne is a common condition caused when hair follicles become plugged with oil and dead skin cells.",
        "patient_explanation_hi": "मुँहासे एक आम समस्या है जो त्वचा के रोमछिद्रों में तेल और मृत त्वचा कोशिकाओं के जमा होने से होती है।",
        "self_care_en": "Wash your face twice daily with a gentle cleanser. Avoid squeezing or popping lesions.",
        "self_care_hi": "चेहरे को दिन में दो बार सौम्य क्लीन्ज़र से धोएं। दानों को नोचने या फोड़ने से बचें।"
    },
    "eczema": {
        "display_name": "Eczema (Atopic Dermatitis)",
        "hindi_name": "एक्जिमा (Eczema / त्वचा की सूजन)",
        "category": "common",
        "is_special": False,
        "is_malignant": False,
        "common_sites": ["flexor creases", "inner elbows", "behind knees", "neck", "hands", "wrists"],
        "typical_symptoms": ["intense itch", "dry skin", "erythema", "scaling", "excoriation"],
        "patient_explanation_en": "Eczema is an inflammatory condition leading to dry, red, and itchy patches of skin.",
        "patient_explanation_hi": "एक्जिमा एक त्वचा विकार है जिसके कारण त्वचा सूखी, लाल और बहुत खुजलीदार हो जाती है।",
        "self_care_en": "Apply moisturizers frequently, use lukewarm water for bathing, and avoid harsh scented soaps.",
        "self_care_hi": "नियमित रूप से मॉइस्चराइज़र लगाएं, गुनगुने पानी से नहाएं और तेज खुशबूदार साबुनों से बचें।"
    },
    "psoriasis": {
        "display_name": "Psoriasis Vulgaris",
        "hindi_name": "सोरायसिस (Psoriasis)",
        "category": "common",
        "is_special": False,
        "is_malignant": False,
        "common_sites": ["extensor surfaces", "elbows", "knees", "scalp", "lower back"],
        "typical_symptoms": ["well-demarcated plaques", "silvery scales", "thickened skin", "mild to moderate itch"],
        "patient_explanation_en": "Psoriasis causes skin cells to multiply rapidly, forming thick red patches covered with silvery scales.",
        "patient_explanation_hi": "सोरायसिस में त्वचा कोशिकाएं तेजी से बनती हैं, जिससे चांदी जैसी सफेद पपड़ीदार लाल चकत्ते बन जाते हैं।",
        "self_care_en": "Keep skin well hydrated with emollient creams. Avoid skin injuries and scratching.",
        "self_care_hi": "त्वचा को मॉइस्चराइज़र से नम रखें और खरोंचने या चोट लगने से बचाएं।"
    },
    "tinea": {
        "display_name": "Tinea (Ringworm / Fungal Infection)",
        "hindi_name": "दाद / फंगल इन्फेक्शन (Tinea / Ringworm)",
        "category": "common",
        "is_special": False,
        "is_malignant": False,
        "common_sites": ["groin", "body", "feet", "scalp", "waist", "between toes"],
        "typical_symptoms": ["annular ring-shaped lesion", "active raised scaly border", "central clearing", "itching"],
        "patient_explanation_en": "Tinea is a superficial fungal infection known for circular, ring-shaped rashes with raised scaly edges.",
        "patient_explanation_hi": "दाद (रिंगवर्म) एक फंगल संक्रमण है जिसमें गोल या छल्लेदार लाल चकत्ते और खुजली होती है।",
        "self_care_en": "Keep affected areas clean and completely dry. Do not share towels or personal clothing.",
        "self_care_hi": "प्रभावित हिस्से को साफ और सूखा रखें। अपने तौलिए और कपड़े दूसरों के साथ साझा न करें।"
    },
    "urticaria": {
        "display_name": "Urticaria (Hives / Allergic Wheals)",
        "hindi_name": "पित्ती / हाइव्स (Urticaria)",
        "category": "common",
        "is_special": False,
        "is_malignant": False,
        "common_sites": ["generalized", "torso", "arms", "legs", "widespread"],
        "typical_symptoms": ["transient wheals", "severe itching", "swelling", "blanching erythema", "comes and goes in hours"],
        "patient_explanation_en": "Urticaria (hives) presents as raised, intensely itchy welts that typically appear and resolve within hours.",
        "patient_explanation_hi": "पित्ती में अचानक त्वचा पर उभरे हुए, अत्यधिक खुजली वाले लाल चकत्ते हो जाते हैं जो कुछ घंटों में बदलते रहते हैं।",
        "self_care_en": "Apply cold compresses to soothe the itch. Avoid overheating, tight clothing, and known allergen triggers.",
        "self_care_hi": "खुजली शांत करने के लिए ठंडी सिकाई करें। टाइट कपड़े और संभावित एलर्जी वाली चीजों से बचें।"
    },
    "scabies": {
        "display_name": "Scabies Infestation",
        "hindi_name": "खुजली / स्केबीज (Scabies)",
        "category": "common",
        "is_special": False,
        "is_malignant": False,
        "common_sites": ["finger web spaces", "wrists", "waistline", "axillae", "groin", "buttocks"],
        "typical_symptoms": ["severe nocturnal itch", "burrows", "papules", "household members affected"],
        "patient_explanation_en": "Scabies is caused by tiny microscopic mites burrowing in the skin, causing severe itching that peaks at night.",
        "patient_explanation_hi": "स्केबीज सूक्ष्म कीड़ों (माइट्स) के कारण होने वाला संक्रमण है, जिसमें रात के समय बहुत तेज खुजली होती है।",
        "self_care_en": "Wash all bed linens and clothing in hot water. Household contacts should be clinically checked together.",
        "self_care_hi": "बिस्तर की चादरें और कपड़े गर्म पानी में धोएं। परिवार के सभी सदस्यों को एक साथ जांच करवानी चाहिए।"
    },
    "possible_malignancy": {
        "display_name": "Possible Skin Malignancy (Urgent Referral)",
        "hindi_name": "संभावित त्वचा असामान्यता (विशेषज्ञ परामर्श अनिवार्य)",
        "category": "special",
        "is_special": True,
        "is_malignant": True,
        "common_sites": ["sun-exposed areas", "face", "neck", "arms", "back", "soles", "palms"],
        "typical_symptoms": ["asymmetry", "border irregularity", "color variegation", "diameter > 6mm", "evolving or bleeding"],
        "patient_explanation_en": "Visual characteristics indicate an atypical lesion that warrants direct examination by a dermatologist.",
        "patient_explanation_hi": "त्वचा पर दिख रहे इस निशान की प्रकृति की तुरंत किसी त्वचा विशेषज्ञ डॉक्टर से प्रत्यक्ष जांच करवानी चाहिए।",
        "self_care_en": "Do not scratch or manipulate the lesion. Protect the area from direct sun exposure until your doctor's visit.",
        "self_care_hi": "निशान को खरोंचे या दबाएं नहीं। जब तक डॉक्टर से जांच न हो, धूप से बचाकर रखें।"
    },
    "other_or_unclear": {
        "display_name": "Other / Non-Conclusive (Referral)",
        "hindi_name": "अन्य या अस्पष्ट स्थिति (डॉक्टर से परामर्श लें)",
        "category": "special",
        "is_special": True,
        "is_malignant": False,
        "common_sites": ["any"],
        "typical_symptoms": ["atypical presentation", "mixed lesions", "uncertain pattern"],
        "patient_explanation_en": "The skin appearance does not clearly match standard benign patterns and requires a comprehensive in-person check.",
        "patient_explanation_hi": "लक्षण सामान्य श्रेणियों से पूरी तरह मेल नहीं खाते हैं। सटीक पहचान के लिए डॉक्टर से जांच करवाना सुरक्षित है।",
        "self_care_en": "Observe for changes and arrange a visit with your physician or skin clinic.",
        "self_care_hi": "लक्षणों पर नज़र रखें और नजदीकी क्लिनिक या डॉक्टर से परामर्श करें।"
    }
}

