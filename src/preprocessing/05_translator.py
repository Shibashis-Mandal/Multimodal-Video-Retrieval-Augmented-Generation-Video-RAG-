# =============================================================================
# Import Required Libraries
# =============================================================================

from deep_translator import GoogleTranslator


# =============================================================================
# Translator Class
# =============================================================================

class Translator:
    """
    Translates Bengali text into English using Google Translator.
    """

    def __init__(self):

        # Initialize translator
        self.translator = GoogleTranslator(
            source="bn",
            target="en"
        )

    # -------------------------------------------------------------------------

    def translate(self, bengali_text):
        """
        Translate Bengali text to English.
        """

        if bengali_text is None:
            return ""

        bengali_text = bengali_text.strip()

        if bengali_text == "":
            return ""

        try:

            english_text = self.translator.translate(
                bengali_text
            )

            return english_text

        except Exception as e:

            print(f"Translation Error: {e}")

            return ""