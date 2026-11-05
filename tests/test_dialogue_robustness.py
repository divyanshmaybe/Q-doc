"""
Rigorous Clinical Dialogue and Reasoner Robustness Tests for Q-Doc MVP.
Tests realistic dermatological complaints, colloquial Hindi/Hinglish/English vocabulary,
morphology extraction, red flags, and multi-turn back-memory tracking.
"""

import unittest
from services.dialogue.schemas import ClinicalIntakeSlots, SkinCondition, ImagePrediction
from services.dialogue.manager import DialogueManager
from services.dialogue.language import detect_language
from services.reasoner.engine import ClinicalReasonerEngine


class TestClinicalRobustness(unittest.TestCase):
    def setUp(self):
        self.dm = DialogueManager(max_turns=6)
        self.reasoner = ClinicalReasonerEngine()

    def test_single_turn_compound_all_slots_filled(self):
        """User states all 5 slots in first utterance."""
        slots = ClinicalIntakeSlots(primary_language="en-IN")
        utterance = "I have an itchy red rash on my legs for 3 days, no fever and nobody in my family has it."
        updated_slots, msg, is_ready, confirm = self.dm.process_turn(slots, utterance)

        self.assertEqual(updated_slots.body_site, "legs")
        self.assertEqual(updated_slots.duration_days, 3)
        self.assertTrue(updated_slots.has_itching)
        self.assertFalse(updated_slots.has_fever)
        self.assertFalse(updated_slots.household_contacts_affected)
        self.assertTrue(is_ready, "All slots filled should immediately signal ready for photo")
        self.assertIn("legs", msg.lower())

    def test_morphology_mirroring_rough_and_flaky(self):
        """User reports 'rough and flaky' skin on face — agent must NOT call it generic rash."""
        slots = ClinicalIntakeSlots(primary_language="en-IN")
        utterance = "My face skin is very rough and flaky."
        updated_slots, msg, is_ready, _ = self.dm.process_turn(slots, utterance)

        self.assertEqual(updated_slots.body_site, "face")
        self.assertEqual(updated_slots.lesion_type, "rough and flaky skin")
        self.assertIn("rough and flaky skin", msg.lower())
        self.assertNotIn("rash on your face", msg.lower())

    def test_colloquial_body_site_inner_thighs_groin(self):
        """Tests colloquial private/groin area vocabulary."""
        slots = ClinicalIntakeSlots(primary_language="en-IN")
        utterance = "I have terrible itching down there between my legs."
        updated_slots, _, _, _ = self.dm.process_turn(slots, utterance)
        self.assertEqual(updated_slots.body_site, "groin")
        self.assertTrue(updated_slots.has_itching)

    def test_colloquial_between_toes_and_feet(self):
        """Tests web spaces of toes mapping to legs/feet."""
        slots = ClinicalIntakeSlots(primary_language="en-IN")
        utterance = "There is cracking skin between my toes."
        updated_slots, _, _, _ = self.dm.process_turn(slots, utterance)
        self.assertEqual(updated_slots.body_site, "legs")

    def test_colloquial_scalp_and_hairline(self):
        """Tests scalp and hairline mapping to face/head."""
        slots = ClinicalIntakeSlots(primary_language="en-IN")
        utterance = "Heavy flaking around my hairline and behind my ears."
        updated_slots, _, _, _ = self.dm.process_turn(slots, utterance)
        self.assertEqual(updated_slots.body_site, "face")

    def test_hindi_daad_ringworm_extraction(self):
        """Tests Hindi fungal complaints (daad/ringworm)."""
        slots = ClinicalIntakeSlots(primary_language="hi-IN")
        utterance = "जांघों में दाद हो गया है और बहुत खुजली होती है दो हफ्ते से"
        updated_slots, _, _, _ = self.dm.process_turn(slots, utterance)
        self.assertEqual(updated_slots.body_site, "legs")  # jaanghon maps to legs
        self.assertEqual(updated_slots.duration_days, 14)
        self.assertTrue(updated_slots.has_itching)

    def test_hinglish_multi_turn_memory(self):
        """Tests persistent memory across multiple turns in Hinglish."""
        slots = ClinicalIntakeSlots(primary_language="hi-IN")

        # Turn 1: site and duration
        slots, msg1, ready1, _ = self.dm.process_turn(slots, "mere haath par 4 din se daane hain", None)
        self.assertEqual(slots.body_site, "hands")
        self.assertEqual(slots.duration_days, 4)
        self.assertFalse(ready1)

        # Turn 2: itching
        slots, msg2, ready2, _ = self.dm.process_turn(slots, "haan bohot khujli hoti hai raat ko", "has_itching")
        self.assertTrue(slots.has_itching)
        self.assertFalse(ready2)

        # Turn 3: fever and contacts
        slots, msg3, ready3, _ = self.dm.process_turn(slots, "bukhar nahi hai aur ghar me sab theek hain kisi ko nahi", "has_fever")
        self.assertFalse(slots.has_fever)
        self.assertFalse(slots.household_contacts_affected)
        self.assertTrue(ready3, "After 3 turns, all 5 slots collected")

    def test_language_detection_and_autoswitch(self):
        """Tests accuracy of detect_language across English, Hindi, and Hinglish."""
        self.assertEqual(detect_language("I have a red rash on my chest", "hi-IN"), "en-IN")
        self.assertEqual(detect_language("mere chehre par bohot khujli hai", "en-IN"), "hi-IN")
        self.assertEqual(detect_language("चेहरे पर मुँहासे हो गए हैं", "en-IN"), "hi-IN")
        self.assertEqual(detect_language("haan bukhar nahi hai", "en-IN"), "hi-IN")
        self.assertEqual(detect_language("yes, for about 2 weeks", "hi-IN"), "en-IN")

    def test_scabies_reasoner_boost(self):
        """Tests Indian clinical scabies boost on wrist + itch + contacts."""
        slots = ClinicalIntakeSlots(
            primary_language="en-IN",
            body_site="hands",
            has_itching=True,
            household_contacts_affected=True,
            duration_days=7
        )
        fake_img = ImagePrediction(
            probabilities={
                SkinCondition.ECZEMA: 0.45,
                SkinCondition.SCABIES: 0.30,
                SkinCondition.ACNE: 0.05,
                SkinCondition.PSORIASIS: 0.05,
                SkinCondition.TINEA: 0.05,
                SkinCondition.URTICARIA: 0.05,
                SkinCondition.POSSIBLE_MALIGNANCY: 0.02,
                SkinCondition.OTHER_UNCLEAR: 0.03,
            },
            top_condition=SkinCondition.ECZEMA,
            confidence=0.45,
            image_quality_score=0.9,
            quality_passed=True
        )
        output = self.reasoner.reason(slots, fake_img)
        self.assertEqual(output.top_diagnosis, SkinCondition.SCABIES, "Voice history should flip top from eczema to scabies")

    def test_melanoma_red_flag_from_spreading_pigment(self):
        """Tests ABCDE criteria recognition triggering referral."""
        slots = ClinicalIntakeSlots(
            primary_language="en-IN",
            body_site="torso",
            lesion_type="dark spot/mole",
            is_spreading=True,
            duration_days=60
        )
        fake_img = ImagePrediction(
            probabilities={
                SkinCondition.ECZEMA: 0.1,
                SkinCondition.SCABIES: 0.05,
                SkinCondition.ACNE: 0.05,
                SkinCondition.PSORIASIS: 0.05,
                SkinCondition.TINEA: 0.05,
                SkinCondition.URTICARIA: 0.05,
                SkinCondition.POSSIBLE_MALIGNANCY: 0.20,
                SkinCondition.OTHER_UNCLEAR: 0.45,
            },
            top_condition=SkinCondition.OTHER_UNCLEAR,
            confidence=0.45,
            image_quality_score=0.9,
            quality_passed=True
        )
        output = self.reasoner.reason(slots, fake_img)
        self.assertIn("possible_malignancy", output.identified_red_flags)
        self.assertEqual(output.top_diagnosis, SkinCondition.POSSIBLE_MALIGNANCY)


if __name__ == "__main__":
    unittest.main()

