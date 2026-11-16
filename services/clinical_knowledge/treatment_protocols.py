"""
Evidence-Based Dermatological Treatment Protocols for Q-Doc MVP.
Provides actionable first-line OTC (Over-The-Counter) active ingredients,
evidence-based self-care regimens, preventive barrier repair, and clear red-flag triggers.
Adheres strictly to IADVL, AAD, and NHS guidelines without dispensing prescription dosages.
"""

from typing import Dict, Any, List
from services.dialogue.schemas import SkinCondition

DERMATOLOGY_TREATMENTS: Dict[SkinCondition, Dict[str, Any]] = {
    SkinCondition.ACNE: {
        "display_name": "Acne Vulgaris",
        "otc_active_ingredients_en": [
            "Salicylic Acid (0.5% - 2%) foaming cleanser to unclog sebum and exfoliate dead cells",
            "Benzoyl Peroxide (2.5% - 5%) wash or gel to reduce Cutibacterium acnes bacteria",
            "Niacinamide (2% - 5%) serum to reduce inflammation and regulate oil secretion",
            "Oil-free, non-comedogenic gel moisturizer"
        ],
        "otc_active_ingredients_hi": [
            "सैलिसिलिक एसिड (0.5% - 2%) क्लीन्ज़र - रोमछिद्रों से अतिरिक्त तेल और मृत त्वचा हटाने के लिए",
            "बेंजोयल पेरोक्साइड (2.5% - 5%) वॉश - मुँहासे के बैक्टीरिया को नष्ट करने के लिए",
            "नियासिनामाइड (2% - 5%) सीरम - त्वचा की सूजन व तेल को नियंत्रित करने के लिए",
            "ऑयल-फ्री नॉन-कॉमेडोजेनिक मॉइस्चराइज़र"
        ],
        "self_care_and_hygiene": {
            "en": "Wash your face twice daily with lukewarm water and a gentle cleanser. Never squeeze, scratch, or pop pimples as this forces bacteria deeper and causes dark hyperpigmented marks or permanent scars. Change pillowcases twice a week and avoid oil-heavy hair pomades.",
            "hi": "दिन में दो बार गुनगुने पानी और सौम्य क्लीन्ज़र से चेहरा धोएं। दानों को नोचने, फोड़ने या दबाने से बचें ताकि काले दाग और गड्ढे न बनें। तकिए का कवर हफ्ते में दो बार बदलें।"
        },
        "when_to_see_doctor": {
            "en": "If deep, painful cystic lumps develop, or if lesions do not improve after 6-8 weeks of consistent OTC skin care.",
            "hi": "यदि चेहरे पर दर्दनाक गांठें बन जाएं या 6-8 हफ्ते में सुधार न दिखे तो त्वचा रोग विशेषज्ञ से मिलें।"
        }
    },

    SkinCondition.ECZEMA: {
        "display_name": "Eczema (Atopic Dermatitis)",
        "otc_active_ingredients_en": [
            "Ceramide-rich barrier repair cream applied within 3 minutes of bathing",
            "Colloidal Oatmeal baths and moisturizing lotions to soothe severe itch",
            "Pure white petroleum jelly (Vaseline) for intensely dry or cracked patches",
            "Mild soap-free, fragrance-free syndet cleansing bars"
        ],
        "otc_active_ingredients_hi": [
            "सिरामाइड युक्त बैरियर रिपेयर क्रीम - नहाने के 3 मिनट के भीतर लगाएं",
            "कोलाइडल ओटमील युक्त लोशन - तेज खुजली और जलन को शांत करने के लिए",
            "सफेद पेट्रोलियम जेली (वैसलीन) - फटी और रूखी त्वचा के लिए",
            "बिना खुशबू वाला माइल्ड सोप-फ्री क्लीन्ज़र"
        ],
        "self_care_and_hygiene": {
            "en": "Take short showers (5-10 minutes) using lukewarm, not hot, water. Immediately lock in moisture with thick creams. Wear loose-fitting, soft 100% cotton clothing. Keep nails trimmed short to prevent skin breakdown during sleep.",
            "hi": "गर्म पानी की जगह गुनगुने पानी से 5-10 मिनट ही नहाएं। नहाने के तुरंत बाद त्वचा पर गाढ़ा मॉइस्चराइज़र लगाएं। ढीले सूती कपड़े पहनें और नाखूनों को छोटा रखें।"
        },
        "when_to_see_doctor": {
            "en": "If skin begins oozing yellow fluid, develops honey-colored crusts (bacterial infection), or prevents sleep.",
            "hi": "यदि चकत्तों से पीला पानी बहने लगे, पीले पपड़ीदार घाव बन जाएं, या खुजली से नींद न आए तो तुरंत डॉक्टर को दिखाएं।"
        }
    },

    SkinCondition.PSORIASIS: {
        "display_name": "Psoriasis Vulgaris",
        "otc_active_ingredients_en": [
            "Salicylic acid (3% - 6%) ointment to soften and descale thick plaques",
            "Coal Tar shampoo (1% - 2%) or body wash to slow down rapid epidermal cell turnover",
            "Dense emollient ointments with liquid paraffin and urea (10%) for intense hydration",
            "Gentle natural sunlight exposure (10-15 minutes in early morning)"
        ],
        "otc_active_ingredients_hi": [
            "सैलिसिलिक एसिड (3% - 6%) ऑइंटमेंट - मोटी पपड़ी को नरम कर हटाने के लिए",
            "कोल टार शैम्पू या वॉश - त्वचा कोशिकाओं के अत्यधिक बढ़ने को धीमा करने के लिए",
            "यूरिया (10%) युक्त गाढ़ा मॉइस्चराइज़र - गहरी नमी प्रदान करने के लिए",
            "सुबह की हल्की धूप में 10-15 मिनट बैठना"
        ],
        "self_care_and_hygiene": {
            "en": "Apply thick moisturizers multiple times throughout the day. Never forcibly peel or scratch off silvery scales, as skin trauma triggers new plaques at the site of injury (Koebner phenomenon). Manage stress and avoid tobacco and alcohol triggers.",
            "hi": "दिन में कई बार गाढ़ा मॉइस्चराइज़र लगाएं। पपड़ी को कभी भी खुरचें या नोचें नहीं, क्योंकि चोट लगने पर नए चकत्ते उभर सकते हैं (कोएब्नर प्रभाव)।"
        },
        "when_to_see_doctor": {
            "en": "If you experience swelling and pain in finger/toe joints, or if plaques spread over large areas of the body.",
            "hi": "यदि जोड़ों में दर्द या सूजन होने लगे, या चकत्ते शरीर के बड़े हिस्से में फैल जाएं तो त्वचा रोग विशेषज्ञ से मिलें।"
        }
    },

    SkinCondition.TINEA: {
        "display_name": "Tinea (Fungal Ringworm / Jock Itch / Athlete's Foot)",
        "otc_active_ingredients_en": [
            "Topical Antifungal Cream: Clotrimazole (1%), Miconazole (2%), or Terbinafine (1%) applied to lesion AND 2cm beyond border",
            "Tolnaftate or Zinc Undecylenate dusting powder for groin/feet to absorb moisture",
            "Antifungal Ketoconazole soap (1% - 2%) during bathing"
        ],
        "otc_active_ingredients_hi": [
            "एंटीफंगल क्रीम: क्लोट्रिमेज़ोल (1%) या टर्बिनाफाइन (1%) - दाद के चकत्ते और उसके 2 सेमी चारों ओर लगाएं",
            "एंटीफंगल डस्टिंग पाउडर - जांघों और पैरों को सूखा रखने के लिए",
            "कीटोकोनाज़ोल सोप (1% - 2%) से नहाना"
        ],
        "self_care_and_hygiene": {
            "en": "Keep the infected area completely dry and clean. Wear clean, loose, breathable cotton undergarments. Never apply over-the-counter mixed steroid creams (such as Betnovate, Quadriderm, or Fourderm) as steroids feed fungal growth and worsen infection. Wash towels and clothes separately.",
            "hi": "प्रभावित हिस्से को हमेशा सूखा और साफ रखें। ढीले सूती कपड़े पहनें। मेडिकल स्टोर से स्टेरॉयड क्रीम (जैसे बेटनोवेट, क्वाड्रिडर्म) कभी न लगाएं, ये दाद को और ज्यादा फैला देती हैं। अपना तौलिया अलग रखें।"
        },
        "when_to_see_doctor": {
            "en": "If the rash does not improve after 2 weeks of consistent antifungal cream, or if it involves the scalp or nails.",
            "hi": "यदि दो हफ्ते तक एंटीफंगल क्रीम लगाने पर भी आराम न मिले, या संक्रमण सिर के बालों व नाखूनों में हो तो डॉक्टर से मिलें।"
        }
    },

    SkinCondition.URTICARIA: {
        "display_name": "Urticaria (Hives / Wheals)",
        "otc_active_ingredients_en": [
            "Second-Generation Non-Drowsy Antihistamines: Cetirizine (10mg) or Fexofenadine (120mg-180mg) to block histamine",
            "Calamine lotion applied topically to soothe itching and cool burning wheals",
            "Cold compresses applied for 10-15 minutes"
        ],
        "otc_active_ingredients_hi": [
            "एंटीहिस्टामाइन (जैसे सेट्रीज़िन या फेक्सोफेनाडाइन) - खुजली और पित्ती को शांत करने के लिए",
            "कैलामाइन लोशन - त्वचा की जलन और खुजली को तुरंत ठंडक देने के लिए",
            "बर्फ या ठंडे पानी की सिकाई (10-15 मिनट)"
        ],
        "self_care_and_hygiene": {
            "en": "Avoid known physical triggers: hot baths, tight binding clothing, excessive friction, and alcohol. Avoid non-essential NSAID painkillers (like ibuprofen, diclofenac, aspirin) which frequently provoke mast cells and trigger hives.",
            "hi": "गर्म पानी से नहाने और टाइट कपड़ों से बचें। दर्द निवारक दवाइयों (जैसे ब्रूफेन, एस्पिरिन) से बचें क्योंकि ये पित्ती को भड़का सकती हैं।"
        },
        "when_to_see_doctor": {
            "en": "EMERGENCY: Seek hospital emergency care immediately if hives are accompanied by swelling of lips, tongue, or difficulty breathing (Anaphylaxis).",
            "hi": "आपातकालीन चेतावनी: यदि पित्ती के साथ होंठ, जीभ, गले में सूजन आए या सांस लेने में तकलीफ हो तो तुरंत नजदीकी अस्पताल के इमरजेंसी विभाग जाएं।"
        }
    },

    SkinCondition.SCABIES: {
        "display_name": "Scabies Infestation",
        "otc_active_ingredients_en": [
            "Permethrin (5%) Cream applied from neck down to the soles of the feet, left on for 8-14 hours before washing off",
            "Calamine lotion to reduce post-treatment allergic pruritus",
            "Oral antihistamine (Cetirizine) to relieve nocturnal itching"
        ],
        "otc_active_ingredients_hi": [
            "पर्मेथ्रिन (5%) क्रीम - गर्दन से लेकर पैरों के पंजों तक पूरे शरीर पर लगाएं और 8-14 घंटे बाद धोएं",
            "कैलामाइन लोशन - खुजली शांत करने के लिए",
            "एंटीहिस्टामाइन - रात की खुजली से आराम के लिए"
        ],
        "self_care_and_hygiene": {
            "en": "CRITICAL: Every single person living in the household or having close bodily contact must undergo treatment at the exact same time, even if they currently have no symptoms. Wash all bed sheets, blankets, and worn clothing in hot water (>50°C) and dry in hot sun.",
            "hi": "अति आवश्यक: परिवार के सभी सदस्यों का एक ही समय पर इलाज होना चाहिए, भले ही किसी को खुजली न हो रही हो। सभी कपड़े और चादरें गर्म पानी में धोकर तेज धूप में सुखाएं।"
        },
        "when_to_see_doctor": {
            "en": "Consult a doctor for prescription confirmation and if itching persists beyond 3-4 weeks after treatment.",
            "hi": "दवा की सही विधि और पुष्टि के लिए डॉक्टर से मिलें, विशेष रूप से यदि इलाज के 3 हफ्ते बाद भी खुजली बनी रहे।"
        }
    },

    SkinCondition.ACANTHOSIS_NIGRICANS: {
        "display_name": "Acanthosis Nigricans",
        "otc_active_ingredients_en": [
            "Urea cream (10% - 20%) to gently hydrate and soften thickened velvety keratin layers",
            "Lactic Acid or Glycolic Acid (5% - 10%) exfoliating lotion applied at bedtime",
            "Salicylic acid cleanser to unclog and smooth flexural folds",
            "Broad-spectrum sunscreen (SPF 50) on exposed neck areas"
        ],
        "otc_active_ingredients_hi": [
            "यूरिया युक्त क्रीम (10% - 20%) - मोटी व मखमली त्वचा को कोमल बनाने के लिए",
            "लैक्टिक एसिड या ग्लाइकोलिक एसिड लोशन - मृत त्वचा को धीरे-धीरे हटाने के लिए",
            "सैलिसिलिक एसिड क्लीन्ज़र - त्वचा की सिलवटों को साफ व चिकना रखने के लिए",
            "धूप से बचाव के लिए सनस्क्रीन"
        ],
        "self_care_and_hygiene": {
            "en": "Never vigorously scrub or rub the darkened skin with rough loofahs or bleaching soaps; physical friction triggers post-inflammatory hyperkeratosis and makes the darkness thicker and darker. Focus on regular exercise, balanced low-glycemic nutrition, and steady weight management.",
            "hi": "त्वचा को लूफा या कठोर साबुन से जोर से न रगड़ें; रगड़ने से त्वचा और अधिक मोटी व काली हो जाती है। संतुलित खान-पान और नियमित व्यायाम से वजन नियंत्रित रखें।"
        },
        "when_to_see_doctor": {
            "en": "Consult a healthcare provider for routine fasting blood glucose, HbA1c, and insulin testing, or if the dark velvety patches appear suddenly and spread rapidly over weeks.",
            "hi": "रक्त शर्करा (शुगर / HbA1c) की जांच के लिए या यदि कालापन अचानक बहुत तेजी से फैलने लगे तो डॉक्टर से सलाह लें।"
        }
    },

    SkinCondition.POSSIBLE_MALIGNANCY: {
        "display_name": "Suspicious Cutaneous Lesion (Possible Malignancy)",
        "otc_active_ingredients_en": [
            "Broad-spectrum high SPF 50+ mineral sunscreen (Zinc Oxide / Titanium Dioxide) to prevent UV damage",
            "Do NOT apply caustic creams, bleaching agents, or attempt home removal"
        ],
        "otc_active_ingredients_hi": [
            "धूप से बचाव के लिए एसपीएफ 50+ सनस्क्रीन लगाएं",
            "घरेलू नुस्खे, चूना या केमिकल क्रीम निशान पर कभी न लगाएं"
        ],
        "self_care_and_hygiene": {
            "en": "Protect the area from sun and physical trauma. Do not scratch, pick, freeze, or use over-the-counter wart removers on suspicious dark moles or non-healing sores.",
            "hi": "निशान को खरोंचने या छीलने से बचें। धूप से बचाएं और तुरंत त्वचा रोग विशेषज्ञ को दिखाएं।"
        },
        "when_to_see_doctor": {
            "en": "MANDATORY: Direct in-person dermatologist consultation for dermoscopy and excisional biopsy. Any growing, changing, bleeding, or irregular dark mole requires professional evaluation.",
            "hi": "अनिवार्य: त्वचा रोग विशेषज्ञ से प्रत्यक्ष जांच करवाएं। किसी भी बदलते या खून बहने वाले तिल की बायोप्सी आवश्यक है।"
        }
    },

    SkinCondition.OTHER_UNCLEAR: {
        "display_name": "Other / Reactive Dermatosis",
        "otc_active_ingredients_en": [
            "Gentle non-scented moisturizer",
            "Calamine lotion for itch relief",
            "Mild syndet cleanser"
        ],
        "otc_active_ingredients_hi": [
            "बिना खुशबू वाला मॉइस्चराइज़र",
            "खुजली शांत करने के लिए कैलामाइन लोशन",
            "सौम्य क्लीन्ज़र"
        ],
        "self_care_and_hygiene": {
            "en": "Keep skin hydrated and avoid harsh chemical irritants. Note any new medications or systemic symptoms.",
            "hi": "त्वचा को नम रखें और तेज केमिकल साबुनों से बचें।"
        },
        "when_to_see_doctor": {
            "en": "Consult a healthcare provider for physical examination and accurate diagnostic classification.",
            "hi": "सटीक पहचान और सही इलाज के लिए डॉक्टर से जांच करवाएं।"
        }
    }
}


def get_treatment_guidance(condition: Any, lang: str = "en") -> str:
    """Returns comprehensive clinical self-care and first-line treatment guidance."""
    is_hi = "hi" in lang.lower()
    t = None
    if condition in DERMATOLOGY_TREATMENTS:
        t = DERMATOLOGY_TREATMENTS[condition]
    else:
        cond_str = str(condition.value if hasattr(condition, "value") else condition).lower().replace(" ", "_")
        for k, v in DERMATOLOGY_TREATMENTS.items():
            k_str = str(k.value if hasattr(k, "value") else k).lower()
            if k_str == cond_str or cond_str in k_str or k_str in cond_str:
                t = v
                break
    if not t:
        t = DERMATOLOGY_TREATMENTS[SkinCondition.OTHER_UNCLEAR]
    
    if is_hi:
        actives = t.get("otc_active_ingredients_hi", [])
        actives_str = " • ".join(actives[:3])
        hygiene = t.get("self_care_and_hygiene", {}).get("hi", "")
        when = t.get("when_to_see_doctor", {}).get("hi", "")
        return (
            f"उपचार व देखभाल के सुझाव:\n"
            f"1. प्राथमिक उपाय: {actives_str}।\n"
            f"2. त्वचा की देखभाल: {hygiene}\n"
            f"3. डॉक्टर से कब मिलें: {when}"
        )
    else:
        actives = t.get("otc_active_ingredients_en", [])
        actives_str = "; ".join(actives[:3])
        hygiene = t.get("self_care_and_hygiene", {}).get("en", "")
        when = t.get("when_to_see_doctor", {}).get("en", "")
        return (
            f"First-line treatment & self-care regimen:\n"
            f"1. Recommended OTC active ingredients: {actives_str}.\n"
            f"2. Daily skin care: {hygiene}\n"
            f"3. Clinical escalation: {when}"
        )


STRUCTURED_CLINICIAN_PRESCRIPTIONS: Dict[str, Dict[str, Any]] = {
    "tinea": {
        "condition_key": "tinea",
        "display_name": "Tinea Corporis / Cruris (Dermatophytosis)",
        "icd10": "B35.4, B35.6",
        "guideline_basis": "IADVL Consensus Guidelines / AAD Practice Guidelines",
        "diagnostic_summary": "Erythematous annular plaque with elevated, active, scaling borders and central clearing; verified superficial fungal etiology.",
        "primary_prescriptions": [
            {
                "drug_name": "Luliconazole Cream",
                "strength": "1% w/w",
                "route": "Topical",
                "dosage_schedule": "Apply once daily (OD) over lesion extending 2 cm beyond advancing border",
                "duration": "2 - 3 weeks (continue 7 days post clinical resolution)",
                "purpose": "First-line topical fungicidal imidazole for dermatophytes",
                "alternatives": "Terbinafine 1% cream OD or Sertaconazole 2% cream BD"
            }
        ],
        "adjunct_supportive": [
            {
                "drug_name": "Clotrimazole / Tolnaftate Dusting Powder",
                "strength": "1% w/w",
                "route": "Topical Powder",
                "dosage_schedule": "Dust over groin/intertriginous skin folds twice daily",
                "duration": "Duration of therapy",
                "purpose": "Absorbs excess moisture and prevents maceration/recurrence"
            },
            {
                "drug_name": "Levocetirizine Tablet",
                "strength": "5 mg",
                "route": "Oral (PO)",
                "dosage_schedule": "1 tablet at bedtime PRN",
                "duration": "5 - 7 days",
                "purpose": "Symptomatic control of pruritus"
            }
        ],
        "refractory_second_line": "If extensive (>3 lesions) or unresponsive to topical therapy: Tab Terbinafine 250 mg OD PO for 2-4 weeks OR Tab Itraconazole 100 mg BD PO with meals for 1-2 weeks. (Baseline LFT recommended).",
        "critical_precautions": [
            "STRICT WARNING: Do NOT prescribe or apply topical corticosteroids (e.g. Clobetasol, Betamethasone, Quadriderm/Fourderm). Corticosteroids suppress local immunity, leading to Tinea Incognito and steroid-resistant widespread dermatophytosis.",
            "Advise patient to complete the full treatment course even if visible erythema clears earlier.",
            "Maintain strict personal hygiene: wash towels and clothing in hot water (>50°C), dry under direct sunlight, and wear loose-fitting cotton clothing."
        ]
    },

    "scabies": {
        "condition_key": "scabies",
        "display_name": "Scabies Infestation (Sarcoptes scabiei)",
        "icd10": "B86",
        "guideline_basis": "CDC / IADVL / British Association of Dermatologists Guidelines",
        "diagnostic_summary": "Intensely pruritic serpiginous burrows and excoriated papules in web spaces, wrists, axillae, and genitalia with nocturnal pruritus surge.",
        "primary_prescriptions": [
            {
                "drug_name": "Permethrin Dermal Cream",
                "strength": "5% w/w",
                "route": "Topical",
                "dosage_schedule": "Thoroughly apply from chin/neck down to toes and soles; leave on for 8 - 14 hours then shower off. Mandatory repeat in 7 days.",
                "duration": "Day 1 and Day 7 application",
                "purpose": "First-line scabicidal neurotoxin targeting mite nervous system",
                "alternatives": "Benzyl Benzoate 25% lotion or Crotamiton 10% cream"
            }
        ],
        "adjunct_supportive": [
            {
                "drug_name": "Hydroxyzine Tablet",
                "strength": "25 mg",
                "route": "Oral (PO)",
                "dosage_schedule": "1 tablet at bedtime for nocturnal itch",
                "duration": "7 - 10 days",
                "purpose": "Sedating H1-blocker for intense post-scabetic allergic pruritus"
            },
            {
                "drug_name": "Calamine Lotion",
                "strength": "Standard",
                "route": "Topical",
                "dosage_schedule": "Apply generously to itchy patches twice daily",
                "duration": "As needed",
                "purpose": "Soothing cutaneous anti-pruritic relief"
            }
        ],
        "refractory_second_line": "Tab Ivermectin 200 mcg/kg single oral dose PO with fatty meal, repeated on Day 14. Essential for institutional outbreaks or crusted (Norwegian) scabies.",
        "critical_precautions": [
            "EPIDEMIOLOGICAL MANDATE: All cohabitants, bedmates, and close household contacts MUST be treated simultaneously on the same night, regardless of whether they have active symptoms.",
            "Decontamination: Wash all clothing, sheets, and towels used in past 4 days in hot water (>50°C) or seal in plastic bags for 72 hours.",
            "In infants < 2 months, permethrin is contraindicated; use Precipitated Sulfur 5-10% in petrolatum for 3 consecutive nights."
        ]
    },

    "acne": {
        "condition_key": "acne",
        "display_name": "Acne Vulgaris",
        "icd10": "L70.0",
        "guideline_basis": "AAD Guidelines for the Management of Acne Vulgaris",
        "diagnostic_summary": "Polymorphic eruption of open/closed comedones, erythematous inflammatory papules, and pustules on pilosebaceous rich areas.",
        "primary_prescriptions": [
            {
                "drug_name": "Benzoyl Peroxide Gel",
                "strength": "2.5% - 5%",
                "route": "Topical",
                "dosage_schedule": "Apply thin film once daily in the evening to affected zones",
                "duration": "8 - 12 weeks",
                "purpose": "Bactericidal against C. acnes; non-antibiotic so prevents bacterial resistance",
                "alternatives": "Azelaic Acid 10% - 20% gel/cream"
            },
            {
                "drug_name": "Adapalene Gel",
                "strength": "0.1%",
                "route": "Topical",
                "dosage_schedule": "Apply a pea-sized amount to entire face at bedtime",
                "duration": "12 weeks / ongoing maintenance",
                "purpose": "Topical retinoid; normalizes follicular desquamation and prevents microcomedones",
                "alternatives": "Tretinoin 0.025% cream or Tazarotene 0.05% gel"
            },
            {
                "drug_name": "Clindamycin Gel",
                "strength": "1%",
                "route": "Topical",
                "dosage_schedule": "Apply in the morning (co-prescribed with Benzoyl Peroxide)",
                "duration": "8 - 12 weeks",
                "purpose": "Suppresses inflammatory papules and Cutibacterium bacterial colonization",
                "alternatives": "Nadifloxacin 1% cream"
            }
        ],
        "adjunct_supportive": [
            {
                "drug_name": "Broad-Spectrum Oil-Free Sunscreen",
                "strength": "SPF 30+ / PA+++",
                "route": "Topical",
                "dosage_schedule": "Apply every morning 20 minutes before sun exposure",
                "duration": "Daily ongoing",
                "purpose": "Prevents photosensitivity and post-inflammatory hyperpigmentation (PIH)"
            }
        ],
        "refractory_second_line": "Moderate-severe inflammatory: Tab Doxycycline 100 mg OD PO for 6-12 weeks. Severe nodulocystic/scarring: Oral Isotretinoin 0.5-1.0 mg/kg/day under strict dermatologist monitoring and teratogenicity protocol.",
        "critical_precautions": [
            "Retinoids are strictly contraindicated during pregnancy due to teratogenicity.",
            "Advise patient never to squeeze, pick, or manipulate lesions to prevent permanent atrophic scars and hyperpigmentation."
        ]
    },

    "eczema": {
        "condition_key": "eczema",
        "display_name": "Atopic Dermatitis / Eczema",
        "icd10": "L20.9",
        "guideline_basis": "AAD / European Task Force on Atopic Dermatitis (ETFAD)",
        "diagnostic_summary": "Pruritic, poorly demarcated erythematous patches with epidermal barrier disruption, excoriations, and lichenification in flexural folds.",
        "primary_prescriptions": [
            {
                "drug_name": "Fluticasone Propionate / Mometasone Cream",
                "strength": "0.05% - 0.1%",
                "route": "Topical",
                "dosage_schedule": "Apply thin layer twice daily to active inflamed lesions during flares",
                "duration": "7 - 14 days then taper to intermittent proactive therapy",
                "purpose": "Mid-potency topical corticosteroid for rapid acute inflammation control",
                "alternatives": "Hydrocortisone 1% cream for face/flexures"
            },
            {
                "drug_name": "Ceramide & Physiological Lipid Barrier Cream",
                "strength": "High-lipid emollient",
                "route": "Topical",
                "dosage_schedule": "Apply liberally 3-4 times daily and immediately within 3 minutes of bathing",
                "duration": "Continuous long-term",
                "purpose": "Primary barrier repair; reduces transepidermal water loss (TEWL) and prevents antigen penetration",
                "alternatives": "Soft white paraffin + Liquid paraffin (50:50) ointment"
            }
        ],
        "adjunct_supportive": [
            {
                "drug_name": "Tacrolimus Ointment",
                "strength": "0.03% - 0.1%",
                "route": "Topical",
                "dosage_schedule": "Apply twice daily for sensitive areas (eyelids, face, neck) as steroid-sparing agent",
                "duration": "Maintenance phase",
                "purpose": "Calcineurin inhibitor; controls inflammation without cutaneous atrophy"
            },
            {
                "drug_name": "Bilastine / Levocetirizine Tablet",
                "strength": "20 mg / 5 mg",
                "route": "Oral (PO)",
                "dosage_schedule": "1 tablet OD (or at night) during flare-ups",
                "duration": "1 - 2 weeks",
                "purpose": "Symptomatic relief of itch-scratch reflex"
            }
        ],
        "refractory_second_line": "Severe recalcitrant atopic dermatitis: Dupilumab 600 mg SC loading dose followed by 300 mg subcutaneous injection every 2 weeks, or oral Cyclosporine 2.5-4 mg/kg/day.",
        "critical_precautions": [
            "Avoid potent fluorinated steroids on face, eyelids, and intertriginous skin folds to prevent steroid-induced skin atrophy and telangiectasia.",
            "Watch for secondary bacterial impetiginization (S. aureus crusting) or viral Eczema Herpeticum (urgent acyclovir required)."
        ]
    },

    "psoriasis": {
        "condition_key": "psoriasis",
        "display_name": "Psoriasis Vulgaris (Chronic Plaque)",
        "icd10": "L40.0",
        "guideline_basis": "AAD-NPF Joint Guidelines / IADVL Guidelines",
        "diagnostic_summary": "Well-demarcated erythematous plaques covered with coarse, micaceous silvery-white scales over extensor surfaces with Auspitz sign.",
        "primary_prescriptions": [
            {
                "drug_name": "Calcipotriol + Betamethasone Dipropionate Ointment",
                "strength": "0.005% / 0.05%",
                "route": "Topical",
                "dosage_schedule": "Apply once daily (OD) to active plaques",
                "duration": "Up to 4 weeks, then step-down maintenance",
                "purpose": "Synergistic dual therapy: Vitamin D3 analogue normalizes epidermal proliferation; corticosteroid suppresses immune inflammation",
                "alternatives": "Clobetasol Propionate 0.05% ointment OD for hyperkeratotic plaques"
            },
            {
                "drug_name": "Salicylic Acid Ointment",
                "strength": "3% - 6%",
                "route": "Topical",
                "dosage_schedule": "Apply once daily in the evening to thick scaling plaques",
                "duration": "1 - 2 weeks",
                "purpose": "Keratolytic agent; eliminates thick scale to allow penetration of topical antipsoriatics",
                "alternatives": "Urea 10% - 20% ointment"
            }
        ],
        "adjunct_supportive": [
            {
                "drug_name": "Coal Tar Solution / Shampoo",
                "strength": "2% - 5%",
                "route": "Topical",
                "dosage_schedule": "Apply to scalp or body lesions 2-3 times weekly",
                "duration": "Ongoing maintenance",
                "purpose": "Antiproliferative and anti-inflammatory agent slowing rapid keratinocyte turnover"
            }
        ],
        "refractory_second_line": "Moderate-to-severe (>10% BSA or psoriatic arthritis): Tab Methotrexate 10-15 mg PO once weekly with Folic Acid 5 mg; or Biologics (Secukinumab 300 mg SC, Ixekizumab, Adalimumab).",
        "critical_precautions": [
            "ABSOLUTE CONTRAINDICATION: NEVER administer oral systemic corticosteroids (e.g. Prednisone, Dexamethasone). Rapid rebound withdrawal can precipitate life-threatening generalized pustular or erythrodermic psoriasis.",
            "Screen all patients for Psoriatic Arthritis (joint pain, morning stiffness, dactylitis, nail pitting)."
        ]
    },

    "urticaria": {
        "condition_key": "urticaria",
        "display_name": "Acute / Chronic Spontaneous Urticaria",
        "icd10": "L50.0, L50.9",
        "guideline_basis": "EAACI/GA²LEN/EDF/WAO International Urticaria Guidelines",
        "diagnostic_summary": "Transient, intensely pruritic, erythematous raised edematous wheals with surrounding flare; individual lesions resolve within 24 hours without scarring.",
        "primary_prescriptions": [
            {
                "drug_name": "Bilastine Tablet (or Fexofenadine / Levocetirizine)",
                "strength": "20 mg (or Fexofenadine 180 mg / Levocetirizine 5 mg)",
                "route": "Oral (PO)",
                "dosage_schedule": "1 tablet once daily in the morning on an empty stomach",
                "duration": "2 - 4 weeks",
                "purpose": "Second-generation non-sedating H1 antihistamine; first-line baseline histamine receptor blockade",
                "alternatives": "Up-dosing titration: Guidelines support escalating up to 4-fold standard dose (e.g. Bilastine 40-80 mg daily) under physician guidance if symptoms persist"
            }
        ],
        "adjunct_supportive": [
            {
                "drug_name": "Calamine Lotion with Menthol",
                "strength": "1% menthol",
                "route": "Topical",
                "dosage_schedule": "Apply to erupting wheals PRN",
                "duration": "As needed",
                "purpose": "Topical evaporative cooling and soothing relief of cutaneous burning"
            },
            {
                "drug_name": "Famotidine Tablet",
                "strength": "20 mg",
                "route": "Oral (PO)",
                "dosage_schedule": "1 tablet twice daily",
                "duration": "1 - 2 weeks",
                "purpose": "H2 receptor antagonist; synergistic mast-cell vascular histamine blockade"
            }
        ],
        "refractory_second_line": "Short rescue burst: Oral Prednisolone 20-40 mg OD for 3-5 days strictly for acute disabling exacerbations. Chronic refractory urticaria: Omalizumab (anti-IgE) 300 mg subcutaneous injection every 4 weeks.",
        "critical_precautions": [
            "ANAPHYLAXIS SENTINEL: Assess immediately for laryngeal edema, stridor, wheezing, lip/tongue swelling, or presyncope. If present, administer intramuscular Epinephrine 0.3-0.5 mg (1:1000) immediately and call emergency services.",
            "Advise patient to avoid NSAIDs (Ibuprofen, Diclofenac, Aspirin) and ACE inhibitors, which trigger or aggravate mast-cell degranulation."
        ]
    },

    "acanthosis_nigricans": {
        "condition_key": "acanthosis_nigricans",
        "display_name": "Acanthosis Nigricans",
        "icd10": "L83",
        "guideline_basis": "AAD Clinical Compendium / Endocrine Society Guidelines",
        "diagnostic_summary": "Symmetrical, hyperpigmented, velvety papillomatous thickening of flexural creases (posterior neck, axillae, groin) driven by hyperinsulinemia/IGF-1 signaling.",
        "primary_prescriptions": [
            {
                "drug_name": "Urea + Lactic Acid Cream",
                "strength": "Urea 10% - 20% + Lactic Acid 5%",
                "route": "Topical",
                "dosage_schedule": "Apply once daily at bedtime to affected velvety skin folds",
                "duration": "8 - 12 weeks",
                "purpose": "Keratolytic and humectant; dissolves intercorneocyte desmosomes and reduces epidermal papillomatosis",
                "alternatives": "Glycolic Acid 6% - 12% cream or Salicylic Acid 6% ointment"
            },
            {
                "drug_name": "Tretinoin Cream",
                "strength": "0.025%",
                "route": "Topical",
                "dosage_schedule": "Apply a thin layer on alternate nights to clean, dry skin",
                "duration": "8 - 12 weeks",
                "purpose": "Topical retinoid; accelerates epidermal turnover and thins thickened stratum corneum",
                "alternatives": "Adapalene 0.1% gel"
            }
        ],
        "adjunct_supportive": [
            {
                "drug_name": "Endocrine & Metabolic Workup Panel",
                "strength": "Diagnostic Test",
                "route": "Laboratory",
                "dosage_schedule": "Fasting Plasma Glucose, HbA1c, Fasting Serum Insulin, Lipid Profile",
                "duration": "Baseline",
                "purpose": "Screens for underlying insulin resistance, Type 2 Diabetes Mellitus, or Polycystic Ovary Syndrome (PCOS)"
            }
        ],
        "refractory_second_line": "Systemic management of underlying insulin resistance: Tab Metformin 500-1000 mg BD PO (under primary physician/endocrinologist guidance). Severe cosmetic cases: Low-dose oral Isotretinoin (10-20 mg/day) or superficial chemical peels.",
        "critical_precautions": [
            "Patients must NOT vigorously scrub, rub, or use abrasive sponges on dark skin folds; friction triggers post-inflammatory hyperkeratosis (Koebner effect) and darkens the lesion.",
            "RED FLAG: Sudden eruptive onset of extensive acanthosis nigricans in non-obese or older patients warrants urgent evaluation for internal malignancy (Malignant Acanthosis Nigricans, most commonly gastric adenocarcinoma)."
        ]
    },

    "possible_malignancy": {
        "condition_key": "possible_malignancy",
        "display_name": "Suspicious Cutaneous Lesion (Possible Melanoma / NMSC)",
        "icd10": "D48.5, C44.9",
        "guideline_basis": "NCCN Clinical Practice Guidelines in Oncology / AAD Guidelines",
        "diagnostic_summary": "Atypical pigmented or ulcerative cutaneous lesion exhibiting ABCDE clinical features, rapid evolution, or friability requiring histopathological exclusion of malignancy.",
        "primary_prescriptions": [
            {
                "drug_name": "URGENT DERMATOLOGY & DERMATOPATHOLOGY REFERRAL",
                "strength": "Diagnostic Procedure",
                "route": "In-Person Clinic",
                "dosage_schedule": "Immediate dermoscopic evaluation and complete narrow excisional biopsy (1 - 3 mm margins)",
                "duration": "Expedited (within 1-2 weeks)",
                "purpose": "Definitive histopathological diagnosis and microstaging (Breslow depth, ulceration status, mitotic rate)",
                "alternatives": "Punch biopsy or deep saucerization only if excisional biopsy not anatomically feasible"
            }
        ],
        "adjunct_supportive": [
            {
                "drug_name": "High SPF 50+ Broad-Spectrum Mineral Sunscreen",
                "strength": "SPF 50+ / PA++++",
                "route": "Topical",
                "dosage_schedule": "Apply daily to sun-exposed areas",
                "duration": "Continuous",
                "purpose": "Shields skin from UVA/UVB radiation and prevents further genomic ultraviolet damage"
            }
        ],
        "refractory_second_line": "Post-biopsy oncological protocol: Wide local excision based on Breslow thickness, Sentinel Lymph Node Biopsy (SLNB), staging CT/PET, and targeted therapy (BRAF/MEK inhibitors) or immunotherapy (PD-1 inhibitors) if indicated.",
        "critical_precautions": [
            "ABSOLUTE CONTRAINDICATION: Do NOT perform cryotherapy, electrocautery, curettage, laser ablation, or apply caustic salves before histopathological diagnosis. Destructive modalities destroy diagnostic architecture and worsen prognosis.",
            "Instruct patient to avoid trauma, picking, or scratching the suspicious lesion."
        ]
    },

    "other_unclear": {
        "condition_key": "other_unclear",
        "display_name": "Unspecified / Reactive Dermatosis",
        "icd10": "L98.9",
        "guideline_basis": "General Dermatological Assessment Protocol",
        "diagnostic_summary": "Cutaneous presentation with atypical or overlapping morphological features requiring formal in-person examination.",
        "primary_prescriptions": [
            {
                "drug_name": "Physiological Ceramide Barrier Repair Cream",
                "strength": "Standard",
                "route": "Topical",
                "dosage_schedule": "Apply twice daily to clean skin",
                "duration": "2 - 4 weeks",
                "purpose": "Soothes irritated cutaneous barrier without masking clinical morphology",
                "alternatives": "Pure White Petroleum Jelly (USP)"
            }
        ],
        "adjunct_supportive": [
            {
                "drug_name": "Calamine Lotion",
                "strength": "Standard",
                "route": "Topical",
                "dosage_schedule": "Apply to pruritic areas as needed",
                "duration": "As needed",
                "purpose": "Antipruritic symptomatic comfort"
            },
            {
                "drug_name": "Levocetirizine Tablet",
                "strength": "5 mg",
                "route": "Oral (PO)",
                "dosage_schedule": "1 tablet at bedtime PRN",
                "duration": "5 - 7 days",
                "purpose": "Symptomatic control of itching"
            }
        ],
        "refractory_second_line": "In-person consultation for direct examination, dermoscopy, skin scraping for KOH fungal mount, patch test, or diagnostic punch biopsy.",
        "critical_precautions": [
            "Avoid empiric prescription of high-potency corticosteroids or antibiotics until definitive morphological classification is established.",
            "Advise immediate clinical evaluation if systemic symptoms (fever, mucosal involvement, joint pain) arise."
        ]
    }
}


def get_clinical_prescription_proposal(condition: Any) -> Dict[str, Any]:
    """
    Returns an evidence-based, structured clinical prescription proposal
    specifically designed for clinician validation, verification, and EMR audit.
    """
    cond_str = str(condition.value if hasattr(condition, "value") else condition).lower().replace(" ", "_")
    if cond_str in STRUCTURED_CLINICIAN_PRESCRIPTIONS:
        return STRUCTURED_CLINICIAN_PRESCRIPTIONS[cond_str]
    
    # Check partial match
    for k, v in STRUCTURED_CLINICIAN_PRESCRIPTIONS.items():
        if k in cond_str or cond_str in k:
            return v
            
    return STRUCTURED_CLINICIAN_PRESCRIPTIONS["other_unclear"]


