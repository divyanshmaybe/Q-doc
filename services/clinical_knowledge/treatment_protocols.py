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

