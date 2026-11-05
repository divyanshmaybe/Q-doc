"""
Dermatology Clinical Knowledge Base (KB) for Q-Doc MVP.
Synthesized from IADVL (Indian Association of Dermatologists, Venereologists and Leprologists),
AAD (American Academy of Dermatology), and BAD clinical guidelines.
Provides exhaustive clinical morphology, anatomical distribution, Fitzpatrick IV-VI considerations,
differential diagnosis matrices, lay synonyms (English/Hindi), and urgent red-flag pathways.
"""

from typing import Dict, Any, List, Optional
from services.dialogue.schemas import SkinCondition

DERMATOLOGY_KNOWLEDGE_BASE: Dict[SkinCondition, Dict[str, Any]] = {
    SkinCondition.ACNE: {
        "condition_id": "acne_vulgaris",
        "name_en": "Acne Vulgaris",
        "name_hi": "मुँहासे (Acne Vulgaris)",
        "icd10": "L70.0",
        "pathophysiology": "Chronic inflammatory dermatosis of the pilosebaceous unit triggered by follicular hyperkeratinization, Cutibacterium acnes colonization, excess sebum production, and local inflammation.",
        "primary_lesions": ["open comedones (blackheads)", "closed comedones (whiteheads)", "inflammatory papules", "pustules"],
        "secondary_lesions": ["nodules", "pseudocysts", "excoriated papules", "post-inflammatory hyperpigmentation (PIH)", "atrophic/hypertrophic scars"],
        "predilection_sites": ["face (cheeks, forehead, chin, nose, jawline)", "chest (sternum)", "upper back", "shoulders"],
        "demographics_india": "Peak onset 12-25 years. Highly prevalent in Indian urban and humid settings. Significant risk of post-inflammatory hyperpigmentation (PIH) in Fitzpatrick types IV-VI.",
        "lay_vocabulary": {
            "en": ["pimples", "breakouts", "zits", "blackheads", "whiteheads", "bumps on face", "blemishes", "spots"],
            "hi": ["मुँहासे", "मुहासे", "फुंसी", "फुंसियां", "पिंपल", "पिंपल्स", "कील-मुहासे", "phunsi", "muhase"]
        },
        "differentiating_questions": [
            "Are there white/black centered bumps or deep painful lumps under the skin?",
            "Do spots leave dark dark stains or marks when they heal?",
            "Are cosmetics or oil-based hair products being applied to the area?"
        ],
        "differentials": [
            {"condition": "Folliculitis", "clue": "Absence of comedones; follicular pustules centered on hair shafts."},
            {"condition": "Rosacea", "clue": "Flushing, telangiectasia, central facial erythema, onset usually >30 years, absence of comedones."},
            {"condition": "Steroid-induced acneform eruption", "clue": "Monomorphic pustules/papules on trunk/face following topical steroid cream usage (common in India)."}
        ],
        "red_flags": ["Severe nodulocystic lesions risking deep disfiguring scarring", "Sudden eruptive onset associated with systemic symptoms"],
        "patient_guidance": {
            "en": "Wash affected areas twice daily with a gentle, non-comedogenic cleanser. Avoid popping, squeezing, or picking lesions as this drives inflammation deeper and leaves dark marks.",
            "hi": "प्रभावित हिस्से को दिन में दो बार सौम्य साबुन या क्लीन्ज़र से धोएं। दानों को नोचने, फोड़ने या दबाने से बचें ताकि काले दाग और गड्ढे न बनें।"
        }
    },

    SkinCondition.ECZEMA: {
        "condition_id": "eczema_atopic_dermatitis",
        "name_en": "Eczema / Atopic Dermatitis",
        "name_hi": "एक्जिमा (Atopic Dermatitis / त्वचा शोथ)",
        "icd10": "L20",
        "pathophysiology": "Complex multifactorial disorder characterized by epidermal skin barrier disruption (filaggrin mutations common), immune dysregulation (Th2 pathway), and pruritus leading to chronic itch-scratch cycle.",
        "primary_lesions": ["erythematous macules/patches", "edematous papules", "tiny intraepidermal vesicles (acute)"],
        "secondary_lesions": ["xerosis (dryness)", "excoriations", "crusting", "oozing/weeping", "lichenification (skin thickening with exaggerated markings)", "fissures"],
        "predilection_sites": ["antecubital fossae (inner elbows)", "popliteal fossae (behind knees)", "wrists", "ankles", "neck", "eyelids", "hands (contact/hand eczema)"],
        "demographics_india": "Prevalent across all pediatric and adult cohorts. Often worse during dry winters in northern India or after contact with detergents/hard water.",
        "lay_vocabulary": {
            "en": ["dry itchy patches", "rough flaky skin", "scaly skin", "cracked skin", "eczema", "weeping skin", "red irritated skin"],
            "hi": ["सूखी और खुजलीदार त्वचा", "पपड़ीदार त्वचा", "फटी त्वचा", "त्वचा की एलर्जी", "रूखापन", "rukhapan", "papdi", "khujli"]
        },
        "differentiating_questions": [
            "Does itching worsen at night or after hot baths?",
            "Do you or close family have a history of asthma, allergic rhinitis (sneezing), or sensitive skin?",
            "Did this flare up after contact with harsh soaps, detergents, cosmetics, or chemicals?"
        ],
        "differentials": [
            {"condition": "Scabies", "clue": "Severe nocturnal itch, household contacts affected, interdigital burrows. Eczema does not spread across household members."},
            {"condition": "Tinea Corporis", "clue": "Tinea displays distinct annular plaques with elevated active scaly borders and central clearing."},
            {"condition": "Psoriasis", "clue": "Psoriasis plaques are thick, well-demarcated with silvery scales on extensor surfaces (elbows/knees)."}
        ],
        "red_flags": ["Secondary bacterial infection (honey-colored crusting / impetiginization)", "Eczema herpeticum (sudden painful umbilicated vesicles with fever)", "Erythroderma (>90% body surface area involvement)"],
        "patient_guidance": {
            "en": "Apply thick fragrance-free emollients/moisturizers immediately within 3 minutes of bathing. Use lukewarm water, mild soap-free cleansers, and wear soft breathable cotton fabrics.",
            "hi": "नहाने के तुरंत बाद 3 मिनट के भीतर बिना खुशबू वाला गाढ़ा मॉइस्चराइज़र लगाएं। गुनगुने पानी का उपयोग करें, तेज साबुन से बचें और सूती कपड़े पहनें।"
        }
    },

    SkinCondition.PSORIASIS: {
        "condition_id": "psoriasis_vulgaris",
        "name_en": "Psoriasis Vulgaris",
        "name_hi": "सोरायसिस (Psoriasis Vulgaris)",
        "icd10": "L40.0",
        "pathophysiology": "Immune-mediated systemic inflammatory disease with IL-23/IL-17 axis activation driving hyperproliferation of keratinocytes (epidermal transit time reduced from 28 days to 3-5 days).",
        "primary_lesions": ["sharply demarcated erythematous plaques", "guttate papules (in guttate variant)"],
        "secondary_lesions": ["silvery-white micaceous scales", "Auspitz sign (pinpoint bleeding on scale removal)", "painful fissures", "nail pitting", "oil-drop discoloration of nails", "subungual hyperkeratosis"],
        "predilection_sites": ["extensor surfaces (knees, elbows)", "lumbosacral region (lower back)", "scalp", "gluteal cleft", "palms and soles (palmoplantar variant)"],
        "demographics_india": "Prevalence in India ranges from 0.44% to 2.8%. Both sexes equally affected. Peak ages 20-30 and 50-60. Often flares in winter.",
        "lay_vocabulary": {
            "en": ["thick red patches", "silvery scales", "flaking scalp", "scaly elbows", "white crusty plaques", "cracking patches"],
            "hi": ["चांदी जैसी सफेद पपड़ी", "मोटे लाल चकत्ते", "सिर में मोटी पपड़ी", "सोरायसिस", "khurand", "safed papdi"]
        },
        "differentiating_questions": [
            "Do the plaques have thick silvery or chalky white flakes on top?",
            "Do you notice joint pain or morning stiffness in fingers, toes, or lower back (psoriatic arthritis)?",
            "Do you see small depressions (pits) or yellow stains on your fingernails?"
        ],
        "differentials": [
            {"condition": "Seborrheic Dermatitis", "clue": "Greasy, yellowish scales on sebum-rich areas (nasolabial folds, eyebrows, scalp); plaques less thick and poorly demarcated."},
            {"condition": "Chronic Eczema / Lichen Simplex", "clue": "Intense paroxysmal itch with indistinct borders and lichenification without silvery scales."},
            {"condition": "Tinea Incognito", "clue": "Often asymmetrical with pustular rim; history of potent topical steroid use."}
        ],
        "red_flags": ["Generalized pustular psoriasis (widespread sterile pustules with high fever)", "Erythrodermic psoriasis (>90% BSA involvement risking hypothermia/sepsis)", "Severe psoriatic arthritis"],
        "patient_guidance": {
            "en": "Keep skin deeply hydrated with dense emollients. Avoid vigorous scratching or peeling scales to prevent the Koebner phenomenon (new lesions forming at scratch sites).",
            "hi": "त्वचा को मॉइस्चराइज़र से नम रखें। पपड़ी को नोचने या खुरचने से बचें, क्योंकि चोट लगने वाली जगह पर नए चकत्ते उभर सकते हैं (कोएब्नर फेनोमेनन)।"
        }
    },

    SkinCondition.TINEA: {
        "condition_id": "tinea_dermatophytosis",
        "name_en": "Tinea / Superficial Dermatophytosis (Ringworm)",
        "name_hi": "दाद / फंगल संक्रमण (Tinea / Ringworm)",
        "icd10": "B35",
        "pathophysiology": "Keratinophilic fungal infection (Trichophyton mentagrophytes, T. rubrum) invading stratum corneum. In India, massive surge in recalcitrant, widespread, steroid-modified dermatophytosis.",
        "primary_lesions": ["annular (ring-shaped) erythematous papules or vesicles at advancing border"],
        "secondary_lesions": ["peripheral scaling", "central clearing", "hyperpigmentation", "maceration (in tinea pedis / intertrigo)"],
        "predilection_sites": ["groin and inner thighs (tinea cruris)", "body trunk and extremities (tinea corporis)", "feet and interdigital spaces (tinea pedis)", "face (tinea faciei)", "scalp (tinea capitis)"],
        "demographics_india": "Massive epidemiological concern in tropical India with high heat and humidity. Heavily aggravated by over-the-counter (OTC) topical steroid/antifungal/antibacterial triple creams (leading to tinea incognito).",
        "lay_vocabulary": {
            "en": ["ringworm", "circular rash", "itchy rings", "jock itch", "athlete's foot", "fungal infection", "round itchy patches"],
            "hi": ["दाद", "गोल लाल दाद", "जांघों में दाद", "फंगल इन्फेक्शन", "खारिश वाला चकत्ता", "daad", "gol chakatta", "fungal"]
        },
        "differentiating_questions": [
            "Are the patches circular or oval with a raised, reddish, active scaly border and clearer center?",
            "Have you used any over-the-counter mixed steroid creams (like four-derm, betnovate, quadriderm)?",
            "Do you work in hot/sweaty conditions, or wear synthetic tight undergarments?"
        ],
        "differentials": [
            {"condition": "Nummular Eczema", "clue": "Coin-shaped plaques with oozing/crusting throughout, lacking central clearing and raised annular borders."},
            {"condition": "Psoriasis", "clue": "Plaques have thicker silvery scales, symmetrical extensor involvement, no central clearing."},
            {"condition": "Pityriasis Rosea", "clue": "Initial herald patch followed by Christmas tree pattern of collarette-scaly ovals along Langer skin cleavage lines."}
        ],
        "red_flags": ["Extensive tinea corporis covering >50% BSA", "Secondary bacterial cellulitis with spreading redness, warmth, fever", "Tinea capitis with boggy swelling and permanent scarring hair loss (kerion)"],
        "patient_guidance": {
            "en": "Keep infected areas clean and completely dry. Wear loose cotton clothing. Never apply over-the-counter steroid creams as they temporarily suppress redness while worsening fungal growth. Do not share towels or clothes.",
            "hi": "संक्रमित हिस्से को हमेशा सूखा और साफ रखें। ढीले सूती कपड़े पहनें। मेडिकल स्टोर से बिना डॉक्टर की पर्ची के स्टेरॉयड क्रीम कभी न लगाएं। अपने तौलिए और कपड़े अलग रखें।"
        }
    },

    SkinCondition.URTICARIA: {
        "condition_id": "urticaria_hives",
        "name_en": "Urticaria (Hives / Wheals)",
        "name_hi": "पित्ती (Urticaria / Hives)",
        "icd10": "L50",
        "pathophysiology": "Cutaneous mast cell degranulation releasing histamine, prostaglandins, and leukotrienes causing transient local dermal edema (wheal) and surrounding vascular dilation (flare).",
        "primary_lesions": ["evanescent wheals (edematous, blanching, erythematous or pale swellings of variable shape)"],
        "secondary_lesions": ["excoriation marks", "angioedema (deep subcutaneous/submucosal swelling of lips, eyelids, genitalia)"],
        "predilection_sites": ["widespread across trunk, extremities, face, pressure sites"],
        "demographics_india": "Affects 15-20% of population at least once in lifetime. Acute form (<6 weeks) often triggered by viral illness, NSAIDs, antibiotics, or food. Chronic form (>6 weeks) frequently autoimmune/idiopathic.",
        "lay_vocabulary": {
            "en": ["hives", "welts", "swollen patches", "allergic swelling", "nettle rash", "raised red bumps that move around"],
            "hi": ["पित्ती", "उभरे हुए लाल चकत्ते", "सूजन", "उलटी पित्ती", "एलर्जी के चकत्ते", "pitti", "soojan", "chakatte"]
        },
        "differentiating_questions": [
            "Do individual red welts appear, itch intensely, and then completely fade or move within 24 hours?",
            "Is there any swelling of your lips, eyelids, tongue, or throat?",
            "Did this start after taking any new painkiller, antibiotic, or food item?"
        ],
        "differentials": [
            {"condition": "Urticarial Vasculitis", "clue": "Individual lesions persist >24-48 hours, cause burning rather than pure itch, leave residual bruise-like purpura."},
            {"condition": "Erythema Multiforme", "clue": "Target/iris lesions (concentric rings), fixed for days, mucosal involvement common."},
            {"condition": "Scabies / Insect bites", "clue": "Papular, persisting for days/weeks, clustered punctum present."}
        ],
        "red_flags": ["ANAPHYLAXIS: Difficulty breathing, throat tightness, swallowing difficulty, dizziness, tongue swelling (EMERGENCY)", "Angioedema compromising airway", "Lesions persisting >48 hours with fever or joint pain"],
        "patient_guidance": {
            "en": "Apply cool compresses to soothe itching. Avoid heat, tight friction, alcohol, spicy foods, and non-essential NSAID painkillers (like ibuprofen/aspirin) which can trigger mast cells. Seek emergency medical care immediately if breathing or throat difficulty occurs.",
            "hi": "खुजली शांत करने के लिए ठंडी सिकाई करें। तेज गर्मी, धूप, टाइट कपड़े और दर्द निवारक दवाओं (जैसे ब्रूफेन) से बचें। यदि सांस लेने या गले में कोई दिक्कत हो तो तुरंत आपातकालीन डॉक्टर के पास जाएं।"
        }
    },

    SkinCondition.SCABIES: {
        "condition_id": "scabies_infestation",
        "name_en": "Scabies Infestation",
        "name_hi": "स्केबीज (Scabies / खाज)",
        "icd10": "B86",
        "pathophysiology": "Infestation by microscopic mite Sarcoptes scabiei var. hominis. Female mite burrows into stratum corneum laying eggs. Pruritus is driven by Type IV delayed hypersensitivity to mite feces, eggs, and proteins (~3-6 weeks after primary infestation).",
        "primary_lesions": ["intraepidermal burrows (fine, wavy, thread-like greyish-white lines 2-15mm)", "small inflammatory papules", "tiny vesicles"],
        "secondary_lesions": ["excoriations", "crusting", "secondary bacterial impetiginization (Staph/Strep)", "post-inflammatory nodules (scabietic nodules on genitals/axillae)"],
        "predilection_sites": ["interdigital web spaces of fingers", "flexor aspects of wrists", "axillary folds", "umbilicus / waistline", "buttocks", "genitalia (scrotum/penis in males)", "areolae (in females)", "ankles and feet"],
        "demographics_india": "Highly prevalent endemic ectoparasitosis in crowded living conditions, hostels, residential schools, and low-resource urban/rural communities across India.",
        "lay_vocabulary": {
            "en": ["severe night itch", "itch between fingers", "itching all over at night", "little bumps on hands", "family member also itching", "scabies"],
            "hi": ["खाज", "रात में तेज खुजली", "उंगलियों के बीच दाने", "कलाई पर खुजली", "परिवार में खुजली", "khaj", "khujli raat me", "ungliyo ke beech"]
        },
        "differentiating_questions": [
            "Does the itching become significantly more intense or unbearable at night when you get into bed?",
            "Are there small itchy bumps or scratch lines between your fingers, on wrists, or around your waist?",
            "Does anyone else in your home, hostel, or close bed partners have similar itching?"
        ],
        "differentials": [
            {"condition": "Atopic Dermatitis", "clue": "Personal/family atopic diathesis, flexural involvement, no web-space burrows, does NOT spread to household contacts."},
            {"condition": "Papular Urticaria", "clue": "Grouped insect bite reactions, typically exposed areas, does not track web spaces or nocturnal cycle."},
            {"condition": "Adverse Cutaneous Drug Reaction", "clue": "Symmetrical sudden maculopapular exanthem closely linked to drug initiation."}
        ],
        "red_flags": ["Crusted / Norwegian Scabies (hyperkeratotic crusts laden with millions of mites, seen in immunocompromised or elderly patients)", "Severe secondary bacterial cellulitis or post-streptococcal glomerulonephritis"],
        "patient_guidance": {
            "en": "Medical prescription treatment is essential. Every single person in the household must be treated at the same time, even if they do not yet have symptoms. Wash all clothes, bed sheets, and towels in hot water and sun-dry thoroughly.",
            "hi": "डॉक्टर की सलाह से सही दवाई लेना अनिवार्य है। घर के सभी सदस्यों का एक साथ इलाज होना चाहिए, भले ही किसी में अभी लक्षण न हों। सभी कपड़े और बिस्तरों को गर्म पानी में धोकर धूप में सुखाएं।"
        }
    },

    SkinCondition.ACANTHOSIS_NIGRICANS: {
        "condition_id": "acanthosis_nigricans",
        "name_en": "Acanthosis Nigricans",
        "name_hi": "एकेन्थोसिस निगरिकन्स (Acanthosis Nigricans / गर्दन व कांख का कालापन)",
        "icd10": "L83",
        "pathophysiology": "Cutaneous manifestation characterized by velvety, papillomatous hyperpigmented thickening of intertriginous flexural skin, primarily driven by insulin resistance stimulating IGF-1 receptors on keratinocytes and dermal fibroblasts.",
        "primary_lesions": ["velvety hyperpigmented plaques", "thickened papillomatous skin", "hyperpigmentation with exaggerated skin markings"],
        "secondary_lesions": ["acrochordons (skin tags)", "maceration in skin folds"],
        "predilection_sites": ["posterior neck", "axillae (underarms)", "groin", "antecubital fossae", "knuckles"],
        "demographics_india": "Extremely common in Indian phenotype with metabolic syndrome, insulin resistance, PCOD, or high carbohydrate intake.",
        "lay_vocabulary": {
            "en": ["dark neck", "velvety dark patches", "black underarms", "thick dark skin on folds", "dark creases"],
            "hi": ["गर्दन पर कालापन", "कांख का कालापन", "मखमली काली त्वचा", "काली लकीरें", "gardan par kalapan", "aankh ka kalapan"]
        },
        "differentiating_questions": [
            "Does the darkened skin feel slightly velvety or thickened to the touch?",
            "Has there been recent weight gain or a personal/family history of diabetes or thyroid?",
            "Does vigorous scrubbing with soap fail to lighten the area?"
        ],
        "differentials": [
            {"condition": "Post-inflammatory hyperpigmentation (PIH)", "clue": "Flat macular hyperpigmentation without velvety thickening or papillomatosis."},
            {"condition": "Tinea versicolor", "clue": "Fine powdery scale on scraping, patchy distribution on trunk."},
            {"condition": "Erythrasma", "clue": "Coral-red fluorescence under Wood's lamp, macerated intertrigo."}
        ],
        "red_flags": ["Sudden eruptive onset in non-obese elderly individual (tripe palms / paraneoplastic sign)"],
        "patient_guidance": {
            "en": "Acanthosis nigricans is a benign skin finding linked to metabolic health and insulin resistance. Avoid vigorous scrubbing or harsh bleaching agents which worsen skin thickening.",
            "hi": "यह त्वचा की एक सौम्य स्थिति है जो इंसुलिन और मेटाबॉलिज्म से जुड़ी होती है। त्वचा को बहुत ज़ोर से रगड़ने या ब्लीच करने से बचें क्योंकि इससे कालापन और बढ़ सकता है।"
        }
    },

    SkinCondition.POSSIBLE_MALIGNANCY: {
        "condition_id": "suspicious_malignancy",
        "name_en": "Suspicious Pigmented / Neoplastic Lesion",
        "name_hi": "संदेहास्पद गांठ या काला तिल (Possible Malignancy)",
        "icd10": "C43 / C44",
        "pathophysiology": "Malignant transformation of melanocytes (Melanoma) or keratinocytes (Basal Cell Carcinoma / Squamous Cell Carcinoma). Melanoma in darker skin tones (Fitzpatrick IV-VI) frequently presents as Acral Lentiginous Melanoma (palms, soles, subungual nail beds).",
        "primary_lesions": ["asymmetric pigmented macule/plaque", "pearly translucent papule/nodule with telangiectasia (BCC)", "keratotic, hyperkeratotic non-healing nodule/ulcer (SCC)"],
        "secondary_lesions": ["border irregularity", "color variegation (shades of brown, black, blue, red, white)", "spontaneous ulceration", "spontaneous bleeding without trauma", "satellite lesions"],
        "predilection_sites": ["sun-exposed areas (face, ears, neck, scalp)", "palms, soles, under nails (acral sites critical in Indian skin tones)", "trunk"],
        "demographics_india": "While cutaneous melanoma incidence is lower in South Asians than Caucasians, mortality is proportionally higher due to delayed detection. Crucially, up to 50% of melanomas in Indian patients are acral lentiginous (palms, soles, nail apparatus).",
        "lay_vocabulary": {
            "en": ["dark spot changing color", "growing mole", "bleeding spot", "non-healing sore", "black mark under nail", "ugly duckling mole", "irregular black spot"],
            "hi": ["बढ़ता हुआ काला तिल", "घाव जो ठीक नहीं हो रहा", "तिल का रंग बदलना", "तिल से खून आना", "काला धब्बा", "kala til", "ghav jo na bhare"]
        },
        "differentiating_questions": [
            "Has this mole or dark spot changed in size, shape, or color over recent months?",
            "Does it have jagged, notched, or blurred irregular edges?",
            "Does it bleed, ooze, itch, or fail to heal on its own?",
            "Is the lesion on the sole of your foot, palm, or under a fingernail/toenail?"
        ],
        "differentials": [
            {"condition": "Seborrheic Keratosis", "clue": "Benign 'stuck-on' warty appearance with horn pseudocysts; stable over years."},
            {"condition": "Benign Melanocytic Nevus", "clue": "Symmetric, uniform brown color, smooth regular border, diameter <6mm, stable."},
            {"condition": "Pyogenic Granuloma", "clue": "Rapidly growing vascular nodule, bleeds easily, benign reactive proliferation."}
        ],
        "red_flags": ["ABCDE criteria met (Asymmetry, Border irregularity, Color variegation, Diameter >6mm, Evolution)", "Ugly Duckling sign (mole that looks completely distinct from all others)", "Non-healing ulcer persisting >4 weeks", "New dark vertical pigmented band under a nail (Hutchinson's nail sign)"],
        "patient_guidance": {
            "en": "This lesion requires direct in-person evaluation by a dermatologist with dermoscopy and potential biopsy. Do not attempt to scratch, freeze, or use home remedies on suspicious moles.",
            "hi": "इस निशान की त्वचा रोग विशेषज्ञ (Dermatologist) द्वारा डर्मोस्कोपी मशीन से प्रत्यक्ष जांच अति आवश्यक है। इसे कुरेदने या घरेलू नुस्खे आजमाने से बचें।"
        }
    },

    SkinCondition.OTHER_UNCLEAR: {
        "condition_id": "other_reactive_unclear",
        "name_en": "Other / Reactive Dermatosis",
        "name_hi": "अन्य / अस्पष्ट त्वचा विकार",
        "icd10": "L99",
        "pathophysiology": "Encompasses reactive exanthems, lichen planus, pityriasis rosea, vitiligo, polymorphous light eruption (PMLE), contact dermatitis, or drug eruptions requiring formal clinical consultation.",
        "primary_lesions": ["variable: papules, macules, plaques, targetoid lesions, hypopigmented patches"],
        "secondary_lesions": ["variable scaling, post-inflammatory hypopigmentation/hyperpigmentation"],
        "predilection_sites": ["variable according to underlying etiology"],
        "demographics_india": "Broad spectrum across Indian primary care. Polymorphous Light Eruption (sun allergy) and Vitiligo are exceptionally common presenting complaints in Indian dermatology clinics.",
        "lay_vocabulary": {
            "en": ["unclear rash", "white spots", "sun allergy", "itching in sunlight", "odd bumps", "mysterious rash"],
            "hi": ["सफेद दाग", "धूप से एलर्जी", "अजीब दाने", "चकत्ते", "safed daag", "dhoop se allergy"]
        },
        "differentiating_questions": [
            "Did the rash appear rapidly after taking a new medication or exposure to sun?",
            "Are there flat-topped violaceous (purplish) itchy shiny bumps on your wrists (Lichen Planus)?",
            "Are there completely white patches without feeling or itching (Vitiligo / Leprosy check)?"
        ],
        "differentials": [
            {"condition": "Lichen Planus", "clue": "6 Ps: Pruritic, Polygonal, Planar, Purple, Papules, Plaques; Wickham striae on oral mucosa."},
            {"condition": "Vitiligo", "clue": "Depigmented milky-white macules with sharp borders; no sensation loss."},
            {"condition": "Hansen's Disease (Leprosy)", "clue": "Hypopigmented or erythematous patch with loss of thermal/pain sensation. Critical primary care differential in India."}
        ],
        "red_flags": ["Rapidly progressive generalized cutaneous eruption", "Mucosal ulceration in mouth, eyes, or genitals", "Accompanied by high fever, joint pain, facial swelling, or peeling skin"],
        "patient_guidance": {
            "en": "Because the presentation does not fit standard common patterns, an in-person clinical examination by a doctor or dermatologist is recommended for precise diagnosis.",
            "hi": "चूंकि यह स्थिति सामान्य श्रेणियों से मेल नहीं खाती, इसलिए सटीक पहचान के लिए डॉक्टर या त्वचा रोग विशेषज्ञ से प्रत्यक्ष जांच करवाना उचित है।"
        }
    }
}


class DermatologyKnowledgeService:
    """Helper service providing rapid clinical querying for dialogue and reasoner."""

    @classmethod
    def get_condition_info(cls, condition: Any) -> Dict[str, Any]:
        if condition in DERMATOLOGY_KNOWLEDGE_BASE:
            return DERMATOLOGY_KNOWLEDGE_BASE[condition]
        cond_str = str(condition.value if hasattr(condition, "value") else condition).lower().replace(" ", "_")
        for k, v in DERMATOLOGY_KNOWLEDGE_BASE.items():
            k_str = str(k.value if hasattr(k, "value") else k).lower()
            if k_str == cond_str or cond_str in k_str or k_str in cond_str:
                return v
        return DERMATOLOGY_KNOWLEDGE_BASE[SkinCondition.OTHER_UNCLEAR]

    @classmethod
    def get_differentials(cls, condition: SkinCondition) -> List[Dict[str, str]]:
        info = cls.get_condition_info(condition)
        return info.get("differentials", [])

    @classmethod
    def get_differentiating_questions(cls, condition: SkinCondition) -> List[str]:
        info = cls.get_condition_info(condition)
        return info.get("differentiating_questions", [])

    @classmethod
    def get_red_flags(cls, condition: SkinCondition) -> List[str]:
        info = cls.get_condition_info(condition)
        return info.get("red_flags", [])

    @classmethod
    def get_lay_vocabulary(cls, condition: SkinCondition, lang: str = "en") -> List[str]:
        info = cls.get_condition_info(condition)
        vocab = info.get("lay_vocabulary", {})
        return vocab.get(lang, vocab.get("en", []))

