# ============================================================
# NEXUS MULTI-LANGUAGE VOICE LISTENER
# ============================================================

import speech_recognition as sr


# ============================================================
# RECOGNIZER
# ============================================================

recognizer = sr.Recognizer()


# ============================================================
# SUPPORTED LANGUAGES
# ============================================================

LANGUAGES = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Kannada": "kn-IN",
    "Tamil": "ta-IN",
}


# ============================================================
# SCRIPT DETECTION
# ============================================================

def detect_script(text):

    for char in text:

        code = ord(char)


        # ----------------------------------------------------
        # DEVANAGARI
        # ----------------------------------------------------

        if 0x0900 <= code <= 0x097F:

            return "Hindi"


        # ----------------------------------------------------
        # KANNADA
        # ----------------------------------------------------

        if 0x0C80 <= code <= 0x0CFF:

            return "Kannada"


        # ----------------------------------------------------
        # TAMIL
        # ----------------------------------------------------

        if 0x0B80 <= code <= 0x0BFF:

            return "Tamil"


    # --------------------------------------------------------
    # LATIN
    # --------------------------------------------------------

    return "English"


# ============================================================
# NORMALIZE COMMON SPEECH VARIATIONS
# ============================================================

def normalize_text(text):

    text = text.strip()

    lower = text.lower()


    # --------------------------------------------------------
    # MOUSE CLICK
    # --------------------------------------------------------

    if lower == "mouse click":

        return "click"


    # --------------------------------------------------------
    # BGM → BGMI
    # Useful for gaming voice commands
    # --------------------------------------------------------

    if lower == "bgm":

        return "BGMI"


    return text


# ============================================================
# SINGLE LANGUAGE RECOGNITION
# ============================================================

def recognize_language(audio, language_code):

    try:

        text = recognizer.recognize_google(
            audio,
            language=language_code
        )

        if text and text.strip():

            return text.strip()

    except sr.UnknownValueError:

        pass

    except sr.RequestError as e:

        print(
            f"NEXUS: Speech service error "
            f"({language_code}): {e}"
        )

    except Exception as e:

        print(
            f"NEXUS: Recognition error "
            f"({language_code}): {e}"
        )


    return ""


# ============================================================
# MULTI-LANGUAGE LISTENER
# ============================================================

def listen():

    with sr.Microphone() as source:

        print(
            "NEXUS: Listening..."
        )

        recognizer.adjust_for_ambient_noise(
            source,
            duration=0.5
        )

        audio = recognizer.listen(
            source
        )


    # ========================================================
    # TRY LANGUAGES
    # ========================================================

    results = []


    for language_name, language_code in LANGUAGES.items():

        text = recognize_language(
            audio,
            language_code
        )

        if text:

            detected_language = detect_script(
                text
            )

            results.append(
                (
                    language_name,
                    detected_language,
                    text
                )
            )


    # ========================================================
    # NO RESULT
    # ========================================================

    if not results:

        print(
            "NEXUS: I didn't understand that."
        )

        return ""


    # ========================================================
    # SELECT RESULT
    # ========================================================

    selected = None


    # --------------------------------------------------------
    # Prefer native-script recognition
    # --------------------------------------------------------

    for result in results:

        language_name = result[0]
        detected_language = result[1]

        if language_name == detected_language:

            selected = result

            break


    # --------------------------------------------------------
    # Otherwise use first valid result
    # --------------------------------------------------------

    if selected is None:

        selected = results[0]


    language_name = selected[0]
    detected_language = selected[1]
    text = selected[2]


    # ========================================================
    # NORMALIZE
    # ========================================================

    text = normalize_text(
        text
    )


    # ========================================================
    # OUTPUT
    # ========================================================

    print(
        f"NEXUS LANGUAGE: {detected_language}"
    )

    print(
        f"NEXUS TEXT: {text}"
    )


    return text