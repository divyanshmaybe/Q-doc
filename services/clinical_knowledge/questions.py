"""Draft discriminating history prompts. Answers remain patient reports."""
QUESTIONS = {
    "acne": ("Have these spots left pits or raised scars?", "क्या इन दानों के बाद गड्ढे या उभरे हुए निशान रह जाते हैं?"),
    "eczema": ("Has this itchy rash gone away and returned before?", "क्या यह खुजली वाला चकत्ता पहले ठीक होकर दोबारा आया है?"),
    "psoriasis": ("Have you had joint pain or stiffness when you wake up?", "क्या सुबह उठने पर जोड़ों में दर्द या अकड़न होती है?"),
    "tinea": ("Which creams have you used on this patch?", "इस चकत्ते पर आपने कौन सी क्रीम लगाई है?"),
    "urticaria": ("How long does one individual raised spot stay in the same place?", "एक उभरा हुआ चकत्ता एक ही जगह कितनी देर रहता है?"),
    "scabies": ("Has anyone you have close contact with developed similar itching?", "क्या आपके निकट संपर्क में किसी और को ऐसी खुजली हुई है?"),
    "acanthosis_nigricans": ("When did you first notice the darkened skin?", "आपने त्वचा का गहरा रंग पहली बार कब देखा?"),
    "vitiligo": ("Have you noticed reduced feeling in the pale patch? Do not test with sharp or hot objects.", "क्या हल्के रंग वाले हिस्से में महसूस करने की क्षमता कम लगी है? नुकीली या गर्म चीज से जांच न करें।"),
    "melasma": ("Have the dark patches changed with sunlight exposure?", "क्या धूप में रहने से गहरे रंग के धब्बों में बदलाव होता है?"),
    "lichen_planus": ("Do you also have sore areas inside your mouth?", "क्या मुंह के अंदर भी दर्द या घाव हैं?"),
    "seborrheic_dermatitis": ("Where else do you notice flaking besides this area?", "इस हिस्से के अलावा और कहां पपड़ी या रूसी होती है?"),
    "contact_dermatitis": ("What new product or material touched this area before the rash began?", "चकत्ता शुरू होने से पहले इस हिस्से पर कौन सा नया उत्पाद या पदार्थ लगा था?"),
    "pityriasis_versicolor": ("Have similar patches appeared on your chest or back?", "क्या छाती या पीठ पर भी ऐसे धब्बे आए हैं?"),
    "pityriasis_rosea": ("Did one larger patch appear before the smaller patches?", "क्या छोटे चकत्तों से पहले एक बड़ा चकत्ता आया था?"),
    "impetigo": ("Are the sores spreading to new areas?", "क्या घाव नए हिस्सों में फैल रहे हैं?"),
    "herpes_zoster": ("Is there any pain or rash near an eye?", "क्या आंख के पास दर्द या चकत्ता है?"),
    "verruca_vulgaris": ("Has this growth changed or bled?", "क्या इस उभार में बदलाव हुआ है या खून आया है?"),
    "alopecia_areata": ("Is the hair loss in separate patches or spread across the scalp?", "बाल अलग-अलग हिस्सों से झड़ रहे हैं या पूरे सिर से?"),
    "cellulitis": ("How quickly has the affected area spread?", "प्रभावित हिस्सा कितनी तेजी से फैला है?"),
    "fixed_drug_eruption": ("Has a patch returned to the same place after taking a medicine?", "क्या दवा लेने के बाद उसी जगह दोबारा चकत्ता आया है?"),
    "pemphigus_vulgaris": ("Are mouth sores making it difficult to drink?", "क्या मुंह के घावों के कारण पानी पीने में कठिनाई है?"),
    "furunculosis": ("Have similar painful lumps occurred before?", "क्या पहले भी ऐसी दर्दनाक गांठें हुई हैं?"),
    "miliaria": ("Did the bumps begin after heat or heavy sweating?", "क्या गर्मी या ज्यादा पसीने के बाद दाने शुरू हुए?"),
    "rosacea": ("Have you noticed any eye discomfort or changes in vision?", "क्या आंख में तकलीफ या देखने में बदलाव हुआ है?"),
    "folliculitis": ("Did the bumps start after shaving or hair removal?", "क्या शेविंग या बाल हटाने के बाद दाने शुरू हुए?"),
    "xerosis": ("Which cleansers or skin products are you using?", "आप कौन से साबुन या त्वचा के उत्पाद इस्तेमाल कर रहे हैं?"),
    "keratosis_pilaris": ("How long have these rough bumps been present?", "ये खुरदरे दाने कितने समय से हैं?"),
    "molluscum_contagiosum": ("Where on the body have these bumps appeared?", "शरीर में किन जगहों पर ये दाने आए हैं?"),
    "onychomycosis": ("Have any other nails changed in the same way?", "क्या दूसरे नाखूनों में भी ऐसा बदलाव हुआ है?"),
    "suspected_leprosy": ("Have you noticed numbness or weakness in your hands or feet?", "क्या हाथ या पैर में सुन्नपन या कमजोरी महसूस हुई है?"),
}


def screening_question(condition_id, language):
    prompts = QUESTIONS.get(condition_id, (
        "What changes have you noticed since this started?", "शुरू होने के बाद से आपने क्या बदलाव देखा है?"))
    return prompts[1 if language.startswith("hi") else 0]
