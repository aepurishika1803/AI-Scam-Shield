import os
import re
import io
from typing import List, Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract

from hindsight_client import Hindsight


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(
    os.path.join(
        os.path.dirname(__file__),
        ".env"
    )
)

HINDSIGHT_API_KEY = os.getenv(
    "HINDSIGHT_API_KEY",
    ""
).strip()

HINDSIGHT_BASE_URL = os.getenv(
    "HINDSIGHT_BASE_URL",
    "https://api.hindsight.vectorize.io"
).strip()

HINDSIGHT_BANK_ID = os.getenv(
    "HINDSIGHT_BANK_ID",
    "ai-scam-shield"
).strip()


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="AI Scam Shield",
    description="AI-powered multilingual scam detection with Hindsight memory",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# HINDSIGHT
# ============================================================

hindsight = None
HINDSIGHT_READY = False
HINDSIGHT_ERROR = None


def initialize_hindsight():

    global hindsight
    global HINDSIGHT_READY
    global HINDSIGHT_ERROR

    if not HINDSIGHT_API_KEY:

        HINDSIGHT_ERROR = (
            "HINDSIGHT_API_KEY is missing from backend/.env"
        )

        print(
            "Hindsight initialization warning:",
            HINDSIGHT_ERROR
        )

        return

    try:

        hindsight = Hindsight(
            base_url=HINDSIGHT_BASE_URL,
            api_key=HINDSIGHT_API_KEY
        )

        HINDSIGHT_READY = True
        HINDSIGHT_ERROR = None

        print("======================================")
        print("Hindsight client initialized")
        print("Hindsight bank:", HINDSIGHT_BANK_ID)
        print("Hindsight URL:", HINDSIGHT_BASE_URL)
        print("======================================")

        try:

            hindsight.create_bank(
                bank_id=HINDSIGHT_BANK_ID,
                name="AI Scam Shield"
            )

            print(
                "Hindsight memory bank created:",
                HINDSIGHT_BANK_ID
            )

        except Exception as bank_error:

            print(
                "Hindsight bank creation:",
                repr(bank_error)
            )

    except Exception as error:

        HINDSIGHT_READY = False
        HINDSIGHT_ERROR = repr(error)

        print(
            "Hindsight initialization error:",
            repr(error)
        )


initialize_hindsight()


# ============================================================
# TRANSLATIONS
# ============================================================

TEXT = {

    "english": {

        "language": "English",

        "high": "HIGH RISK",
        "medium": "MEDIUM RISK",
        "low": "LOW RISK",

        "high_explanation":
            "This message contains multiple indicators commonly associated with scams or phishing.",

        "medium_explanation":
            "This message contains some suspicious indicators and should be verified carefully.",

        "low_explanation":
            "No major scam indicators were detected.",

        "recommendation_high":
            "Do not click links, share OTPs, passwords, PINs, or banking information. Verify the request using an official channel.",

        "recommendation_medium":
            "Do not act immediately. Verify the sender and request through an official channel.",

        "recommendation_low":
            "No immediate scam action is indicated. Continue to avoid sharing sensitive information.",

        "safe_reply":
            "I will not share OTPs or sensitive information. I will verify this request through the official channel.",

        "memory_active":
            "Hindsight memory is active.",

        "memory_inactive":
            "Hindsight memory is inactive because the memory service could not be reached.",

        "memory_match":
            "Similar scam cases were recalled from Hindsight memory.",

        "memory_no_match":
            "Hindsight recalled successfully, but no closely matching scam case was found.",

        "memory_risk_used":
            "Hindsight recalled similar scam cases, strengthening the evidence for this risk assessment.",

        "memory_no_match_risk":
            "Hindsight memory was successfully checked. No matching case was found, but the current message itself contains strong scam indicators.",

        "memory_medium_reasoning":
            "Hindsight memory was successfully checked and used as additional context for this assessment.",

        "memory_low_reasoning":
            "Hindsight memory was successfully checked. No matching scam pattern was found, so memory did not increase the risk.",

        "memory_error_risk":
            "The current message contains strong scam indicators. Hindsight could not be used because the memory service returned an error.",

        "memory_error_safe":
            "Hindsight could not be used because the memory service returned an error.",

        "otp": "OTP request",
        "urgency": "Urgency",
        "threat": "Threat / fear",
        "bank": "Bank impersonation",
        "verification": "Account verification",
        "suspicious_url": "Suspicious URL",

        "url_detected": "URL detected",
        "url_suspicious": "Suspicious URL indicators detected",
        "no_url": "No URL detected",

        "checklist": [
            "Do not click suspicious links.",
            "Never share OTP, PIN, password, or CVV.",
            "Verify the sender through an official channel.",
            "Do not make payments because of urgency or threats.",
            "Report suspicious messages to the relevant platform or authority."
        ]
    },

    "hindi": {

        "language": "Hindi",

        "high": "उच्च जोखिम",
        "medium": "मध्यम जोखिम",
        "low": "कम जोखिम",

        "high_explanation":
            "इस संदेश में धोखाधड़ी या फ़िशिंग से जुड़े कई संकेत पाए गए हैं।",

        "medium_explanation":
            "इस संदेश में कुछ संदिग्ध संकेत पाए गए हैं। सावधानी से सत्यापन करें।",

        "low_explanation":
            "धोखाधड़ी के कोई प्रमुख संकेत नहीं मिले।",

        "recommendation_high":
            "लिंक पर क्लिक न करें और OTP, पासवर्ड, PIN या बैंकिंग जानकारी साझा न करें। आधिकारिक माध्यम से सत्यापन करें।",

        "recommendation_medium":
            "तुरंत कार्रवाई न करें। आधिकारिक माध्यम से प्रेषक और अनुरोध की पुष्टि करें।",

        "recommendation_low":
            "तत्काल धोखाधड़ी का कोई स्पष्ट संकेत नहीं मिला। फिर भी संवेदनशील जानकारी साझा करने से बचें।",

        "safe_reply":
            "मैं OTP या संवेदनशील जानकारी साझा नहीं करूंगा। मैं आधिकारिक माध्यम से इस अनुरोध की पुष्टि करूंगा।",

        "memory_active":
            "Hindsight मेमोरी सक्रिय है।",

        "memory_inactive":
            "Hindsight मेमोरी निष्क्रिय है क्योंकि मेमोरी सेवा से संपर्क नहीं हो सका।",

        "memory_match":
            "Hindsight मेमोरी में इसी तरह के धोखाधड़ी मामले मिले।",

        "memory_no_match":
            "Hindsight से सफलतापूर्वक जानकारी प्राप्त हुई, लेकिन कोई बहुत मिलता-जुलता धोखाधड़ी मामला नहीं मिला।",

        "memory_risk_used":
            "Hindsight में इसी तरह के धोखाधड़ी मामले मिले, जिससे वर्तमान जोखिम के लिए अतिरिक्त प्रमाण मिला।",

        "memory_no_match_risk":
            "Hindsight मेमोरी सफलतापूर्वक जांची गई। कोई समान मामला नहीं मिला, लेकिन वर्तमान संदेश में स्वयं मजबूत धोखाधड़ी संकेत हैं।",

        "memory_medium_reasoning":
            "Hindsight मेमोरी सफलतापूर्वक जांची गई और इस जोखिम मूल्यांकन के लिए अतिरिक्त संदर्भ के रूप में उपयोग की गई।",

        "memory_low_reasoning":
            "Hindsight मेमोरी सफलतापूर्वक जांची गई। कोई समान धोखाधड़ी पैटर्न नहीं मिला, इसलिए मेमोरी ने जोखिम नहीं बढ़ाया।",

        "memory_error_risk":
            "वर्तमान संदेश में मजबूत धोखाधड़ी संकेत हैं। Hindsight का उपयोग नहीं हो सका क्योंकि मेमोरी सेवा ने त्रुटि दी।",

        "memory_error_safe":
            "Hindsight का उपयोग नहीं हो सका क्योंकि मेमोरी सेवा ने त्रुटि दी।",

        "otp": "OTP अनुरोध",
        "urgency": "तत्कालता",
        "threat": "डर / धमकी",
        "bank": "बैंक प्रतिरूपण",
        "verification": "खाता सत्यापन",
        "suspicious_url": "संदिग्ध URL",

        "url_detected": "URL मिला",
        "url_suspicious": "संदिग्ध URL संकेत मिले",
        "no_url": "कोई URL नहीं मिला",

        "checklist": [
            "संदिग्ध लिंक पर क्लिक न करें।",
            "OTP, PIN, पासवर्ड या CVV कभी साझा न करें।",
            "आधिकारिक माध्यम से प्रेषक की पुष्टि करें।",
            "डर या जल्दबाजी के कारण भुगतान न करें।",
            "संदिग्ध संदेश को संबंधित प्लेटफॉर्म या प्राधिकरण को रिपोर्ट करें।"
        ]
    },

    "telugu": {

        "language": "Telugu",

        "high": "అధిక ప్రమాదం",
        "medium": "మధ్యస్థ ప్రమాదం",
        "low": "తక్కువ ప్రమాదం",

        "high_explanation":
            "ఈ సందేశంలో మోసం లేదా ఫిషింగ్‌కు సంబంధించిన అనేక ప్రమాద సంకేతాలు ఉన్నాయి.",

        "medium_explanation":
            "ఈ సందేశంలో కొన్ని అనుమానాస్పద సంకేతాలు ఉన్నాయి. జాగ్రత్తగా ధృవీకరించండి.",

        "low_explanation":
            "ప్రధానమైన మోస సంకేతాలు గుర్తించబడలేదు.",

        "recommendation_high":
            "లింక్‌పై క్లిక్ చేయవద్దు. OTP, పాస్‌వర్డ్, PIN లేదా బ్యాంకింగ్ సమాచారాన్ని పంచుకోవద్దు. అధికారిక మార్గం ద్వారా ధృవీకరించండి.",

        "recommendation_medium":
            "వెంటనే చర్య తీసుకోవద్దు. అధికారిక మార్గం ద్వారా పంపిన వ్యక్తి మరియు అభ్యర్థనను ధృవీకరించండి.",

        "recommendation_low":
            "తక్షణ మోస సంకేతాలు కనిపించలేదు. అయినప్పటికీ సున్నితమైన సమాచారాన్ని పంచుకోవద్దు.",

        "safe_reply":
            "నేను OTP లేదా సున్నితమైన సమాచారాన్ని పంచుకోను. అధికారిక మార్గం ద్వారా ఈ అభ్యర్థనను ధృవీకరిస్తాను.",

        "memory_active":
            "Hindsight మెమరీ సక్రియంగా ఉంది.",

        "memory_inactive":
            "Hindsight మెమరీ సక్రియంగా లేదు. మెమరీ సేవను చేరుకోలేకపోయాము.",

        "memory_match":
            "Hindsight మెమరీలో ఇలాంటి మోస కేసులు గుర్తించబడ్డాయి.",

        "memory_no_match":
            "Hindsight విజయవంతంగా తనిఖీ చేయబడింది, కానీ దగ్గరగా సరిపోలే మోస కేసు కనుగొనబడలేదు.",

        "memory_risk_used":
            "Hindsightలో ఇలాంటి మోస కేసులు గుర్తించబడ్డాయి. ఇది ప్రస్తుత ప్రమాద అంచనాకు అదనపు ఆధారాన్ని అందించింది.",

        "memory_no_match_risk":
            "Hindsight మెమరీ విజయవంతంగా తనిఖీ చేయబడింది. సరిపోలే కేసు లేదు, కానీ ప్రస్తుత సందేశంలోనే బలమైన మోస సంకేతాలు ఉన్నాయి.",

        "memory_medium_reasoning":
            "Hindsight మెమరీ విజయవంతంగా తనిఖీ చేయబడింది మరియు ఈ ప్రమాద అంచనాకు అదనపు సందర్భంగా ఉపయోగించబడింది.",

        "memory_low_reasoning":
            "Hindsight మెమరీ విజయవంతంగా తనిఖీ చేయబడింది. సరిపోలే మోస నమూనా కనుగొనబడలేదు, కాబట్టి మెమరీ ప్రమాదాన్ని పెంచలేదు.",

        "memory_error_risk":
            "ప్రస్తుత సందేశంలో బలమైన మోస సంకేతాలు ఉన్నాయి. మెమరీ సేవలో లోపం కారణంగా Hindsight ఉపయోగించబడలేదు.",

        "memory_error_safe":
            "మెమరీ సేవలో లోపం కారణంగా Hindsight ఉపయోగించబడలేదు.",

        "otp": "OTP అభ్యర్థన",
        "urgency": "అత్యవసరత",
        "threat": "భయం / బెదిరింపు",
        "bank": "బ్యాంక్ వేషధారణ",
        "verification": "ఖాతా ధృవీకరణ",
        "suspicious_url": "అనుమానాస్పద URL",

        "url_detected": "URL గుర్తించబడింది",
        "url_suspicious": "అనుమానాస్పద URL సంకేతాలు గుర్తించబడ్డాయి",
        "no_url": "URL గుర్తించబడలేదు",

        "checklist": [
            "అనుమానాస్పద లింక్‌లపై క్లిక్ చేయవద్దు.",
            "OTP, PIN, పాస్‌వర్డ్ లేదా CVV ఎప్పుడూ పంచుకోవద్దు.",
            "అధికారిక మార్గం ద్వారా పంపిన వ్యక్తిని ధృవీకరించండి.",
            "భయం లేదా అత్యవసరత కారణంగా డబ్బు పంపవద్దు.",
            "అనుమానాస్పద సందేశాన్ని సంబంధిత ప్లాట్‌ఫారమ్ లేదా అధికారికి రిపోర్ట్ చేయండి."
        ]
    }
}


# ============================================================
# SCAM KEYWORDS
# ============================================================

SCAM_KEYWORDS = {

    "english": {

        "otp": [
            "otp",
            "one time password",
            "verification code",
            "security code"
        ],

        "urgency": [
            "urgent",
            "immediately",
            "act now",
            "right now",
            "within 24 hours",
            "hurry",
            "quickly",
            "expires today"
        ],

        "threat": [
            "blocked",
            "account will be closed",
            "legal action",
            "police",
            "arrest",
            "penalty",
            "suspended",
            "deactivated"
        ],

        "bank": [
            "bank",
            "bank account",
            "credit card",
            "debit card",
            "upi",
            "paypal",
            "wallet"
        ],

        "verification": [
            "verify your account",
            "verify account",
            "account verification",
            "confirm your identity",
            "kyc",
            "verification"
        ],

        "action": [
            "click the link",
            "click here",
            "send",
            "share",
            "enter your",
            "login",
            "sign in"
        ]
    },

    "hindi": {

        "otp": [
            "otp",
            "ओटीपी",
            "वन टाइम पासवर्ड",
            "सुरक्षा कोड"
        ],

        "urgency": [
            "तुरंत",
            "अभी",
            "जल्दी",
            "शीघ्र",
            "फौरन",
            "तत्काल"
        ],

        "threat": [
            "ब्लॉक",
            "ब्लॉक हो गया",
            "बंद हो जाएगा",
            "पुलिस",
            "गिरफ्तार",
            "कानूनी कार्रवाई",
            "जुर्माना",
            "निलंबित"
        ],

        "bank": [
            "बैंक",
            "बैंक खाता",
            "खाता",
            "डेबिट कार्ड",
            "क्रेडिट कार्ड",
            "यूपीआई"
        ],

        "verification": [
            "सत्यापन",
            "सत्यापित",
            "खाता सत्यापन",
            "पहचान सत्यापन",
            "केवाईसी"
        ],

        "action": [
            "लिंक पर क्लिक",
            "क्लिक करें",
            "भेजें",
            "शेयर करें",
            "दर्ज करें",
            "लॉगिन"
        ]
    },

    "telugu": {

        "otp": [
            "otp",
            "ఓటీపీ",
            "ఒటిపి",
            "వన్ టైమ్ పాస్‌వర్డ్"
        ],

        "urgency": [
            "వెంటనే",
            "ఇప్పుడే",
            "త్వరగా",
            "తక్షణం",
            "అత్యవసరం"
        ],

        "threat": [
            "బ్లాక్",
            "బ్లాక్ అవుతుంది",
            "మూసివేయబడుతుంది",
            "పోలీసులు",
            "చట్టపరమైన చర్య",
            "జరిమానా",
            "నిలిపివేయబడింది"
        ],

        "bank": [
            "బ్యాంక్",
            "బ్యాంక్ ఖాతా",
            "ఖాతా",
            "డెబిట్ కార్డు",
            "క్రెడిట్ కార్డు",
            "యూపీఐ"
        ],

        "verification": [
            "ధృవీకరించండి",
            "ధృవీకరణ",
            "ఖాతా ధృవీకరణ",
            "గుర్తింపు ధృవీకరణ",
            "కేవైసీ"
        ],

        "action": [
            "లింక్‌పై క్లిక్",
            "క్లిక్ చేయండి",
            "పంపండి",
            "షేర్ చేయండి",
            "నమోదు చేయండి",
            "లాగిన్"
        ]
    }
}


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def detect_language(text: str) -> str:

    if not text:
        return "english"

    telugu_chars = len(
        re.findall(
            r"[\u0C00-\u0C7F]",
            text
        )
    )

    hindi_chars = len(
        re.findall(
            r"[\u0900-\u097F]",
            text
        )
    )

    if telugu_chars >= 2:
        return "telugu"

    if hindi_chars >= 2:
        return "hindi"

    return "english"


# ============================================================
# URL FUNCTIONS
# ============================================================

def extract_urls(text: str) -> List[str]:

    pattern = r"https?://[^\s<>\"]+"

    return re.findall(
        pattern,
        text,
        flags=re.IGNORECASE
    )


def suspicious_url_keywords(
    url: str
) -> List[str]:

    keywords = [
        "login",
        "verify",
        "verification",
        "secure",
        "security",
        "bank",
        "account",
        "update",
        "confirm",
        "password",
        "wallet",
        "otp",
        "kyc",
        "signin",
        "unlock"
    ]

    url_lower = url.lower()

    return [
        keyword
        for keyword in keywords
        if keyword in url_lower
    ]


# ============================================================
# PATTERN DETECTION
# ============================================================

def detect_patterns(
    message: str,
    language: str
) -> List[str]:

    lower_message = message.lower()

    patterns = []

    keyword_groups = SCAM_KEYWORDS[language]

    for category, keywords in keyword_groups.items():

        for keyword in keywords:

            if keyword.lower() in lower_message:

                if keyword not in patterns:
                    patterns.append(keyword)

    return patterns


# ============================================================
# SCAM DNA
# ============================================================

def calculate_dna(
    message: str,
    language: str,
    urls: List[str]
) -> Dict[str, int]:

    lower_message = message.lower()

    groups = SCAM_KEYWORDS[language]

    otp_score = 0
    urgency_score = 0
    threat_score = 0
    bank_score = 0
    suspicious_url_score = 0

    for word in groups["otp"]:

        if word.lower() in lower_message:
            otp_score = 2
            break

    for word in groups["urgency"]:

        if word.lower() in lower_message:
            urgency_score = 3
            break

    for word in groups["threat"]:

        if word.lower() in lower_message:
            threat_score = 2
            break

    for word in groups["bank"]:

        if word.lower() in lower_message:
            bank_score = 1
            break

    for url in urls:

        if suspicious_url_keywords(url):

            suspicious_url_score = 2
            break

    return {

        "urgency":
            urgency_score,

        "threat":
            threat_score,

        "otp":
            otp_score,

        "bank":
            bank_score,

        "suspicious_url":
            suspicious_url_score
    }


# ============================================================
# RISK CALCULATION
# ============================================================

def calculate_risk(
    patterns: List[str],
    dna: Dict[str, int],
    urls: List[str],
    suspicious_urls: List[str]
) -> int:

    score = 0

    if dna["otp"] > 0:
        score += 25

    if dna["urgency"] > 0:
        score += 20

    if dna["threat"] > 0:
        score += 20

    if dna["bank"] > 0:
        score += 15

    if dna["suspicious_url"] > 0:
        score += 20

    if len(patterns) >= 5:
        score += 15

    if len(patterns) >= 8:
        score += 10

    if urls:
        score += 10

    if suspicious_urls:
        score += 15

    return min(
        score,
        100
    )


# ============================================================
# RISK LEVEL
# ============================================================

def get_risk_level(
    score: int
) -> str:

    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


# ============================================================
# HINDSIGHT MEMORY
# ============================================================

def analyze_hindsight(
    message: str,
    language: str,
    risk_score: int,
    risk_level: str,
    detected_patterns: List[str]
) -> Dict[str, Any]:

    localized = TEXT[language]

    if not HINDSIGHT_READY or hindsight is None:

        if risk_score >= 70:
            reasoning = localized[
                "memory_error_risk"
            ]
        else:
            reasoning = localized[
                "memory_error_safe"
            ]

        return {

            "memory_used":
                False,

            "memory_match":
                False,

            "memory_status":
                "inactive",

            "memory_message":
                localized[
                    "memory_inactive"
                ],

            "memory_match_message":
                localized[
                    "memory_inactive"
                ],

            "memory_reasoning":
                reasoning,

            "memory_recall_error":
                HINDSIGHT_ERROR,

            "memory_retain_success":
                False,

            "memory_retain_error":
                HINDSIGHT_ERROR
        }

    memory_used = False
    memory_match = False

    recall_error = None

    # --------------------------------------------------------
    # RECALL
    # --------------------------------------------------------

    try:

        recall_result = hindsight.recall(
            bank_id=HINDSIGHT_BANK_ID,
            query=message
        )

        memory_results = getattr(
            recall_result,
            "results",
            []
        )

        memory_used = True

        if memory_results:

            memory_match = True

            memory_match_message = localized[
                "memory_match"
            ]

        else:

            memory_match = False

            memory_match_message = localized[
                "memory_no_match"
            ]

        if risk_score >= 70:

            if memory_match:

                reasoning = localized[
                    "memory_risk_used"
                ]

            else:

                reasoning = localized[
                    "memory_no_match_risk"
                ]

        elif risk_score >= 40:

            reasoning = localized[
                "memory_medium_reasoning"
            ]

        else:

            reasoning = localized[
                "memory_low_reasoning"
            ]

    except Exception as error:

        print(
            "Hindsight recall error:",
            repr(error)
        )

        recall_error = repr(error)

        memory_used = False
        memory_match = False

        memory_match_message = localized[
            "memory_inactive"
        ]

        if risk_score >= 70:

            reasoning = localized[
                "memory_error_risk"
            ]

        else:

            reasoning = localized[
                "memory_error_safe"
            ]

    # --------------------------------------------------------
    # RETAIN
    # --------------------------------------------------------

    retain_success = False
    retain_error = None

    try:

        hindsight.retain(
            bank_id=HINDSIGHT_BANK_ID,
            content=(
                "AI Scam Shield analysis case. "
                f"Language: {language}. "
                f"Risk score: {risk_score}/100. "
                f"Risk level: {risk_level}. "
                f"Detected patterns: "
                f"{', '.join(detected_patterns)}. "
                f"Message: {message}"
            )
        )

        retain_success = True

        print(
            "Hindsight retain successful."
        )

    except Exception as error:

        retain_error = repr(error)

        print(
            "Hindsight retain error:",
            repr(error)
        )

    return {

        "memory_used":
            memory_used,

        "memory_match":
            memory_match,

        "memory_status":
            "active" if memory_used else "inactive",

        "memory_message":
            localized[
                "memory_active"
            ] if memory_used else localized[
                "memory_inactive"
            ],

        "memory_match_message":
            memory_match_message,

        "memory_reasoning":
            reasoning,

        "memory_recall_error":
            recall_error,

        "memory_retain_success":
            retain_success,

        "memory_retain_error":
            retain_error
    }


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_scam(
    message: str
) -> Dict[str, Any]:

    message = (
        message or ""
    ).strip()

    language = detect_language(
        message
    )

    localized = TEXT[
        language
    ]

    detected_patterns = detect_patterns(
        message,
        language
    )

    urls = extract_urls(
        message
    )

    suspicious_urls = []

    for url in urls:

        suspicious = suspicious_url_keywords(
            url
        )

        for item in suspicious:

            if item not in suspicious_urls:

                suspicious_urls.append(
                    item
                )

    dna = calculate_dna(
        message,
        language,
        urls
    )

    risk_score = calculate_risk(
        detected_patterns,
        dna,
        urls,
        suspicious_urls
    )

    risk_level = get_risk_level(
        risk_score
    )

    if risk_level == "HIGH":

        explanation = localized[
            "high_explanation"
        ]

        recommendation = localized[
            "recommendation_high"
        ]

    elif risk_level == "MEDIUM":

        explanation = localized[
            "medium_explanation"
        ]

        recommendation = localized[
            "recommendation_medium"
        ]

    else:

        explanation = localized[
            "low_explanation"
        ]

        recommendation = localized[
            "recommendation_low"
        ]

    memory = analyze_hindsight(
        message=message,
        language=language,
        risk_score=risk_score,
        risk_level=risk_level,
        detected_patterns=detected_patterns
    )

    if urls:

        if suspicious_urls:

            url_status = localized[
                "url_suspicious"
            ]

        else:

            url_status = localized[
                "url_detected"
            ]

    else:

        url_status = localized[
            "no_url"
        ]

    return {

        "message":
            message,

        "language":
            language,

        "language_name":
            localized[
                "language"
            ],

        "risk_score":
            risk_score,

        "risk_level":
            risk_level,

        "risk_label":
            localized[
                risk_level.lower()
            ],

        "explanation":
            explanation,

        "detected_patterns":
            detected_patterns,

        "urls":
            urls,

        "suspicious_url_keywords":
            suspicious_urls,

        "url_status":
            url_status,

        "recommendation":
            recommendation,

        "safe_reply":
            localized[
                "safe_reply"
            ],

        "protection_checklist":
            localized[
                "checklist"
            ],

        "scam_dna": {

            "urgency":
                dna["urgency"],

            "threat":
                dna["threat"],

            "otp":
                dna["otp"],

            "bank":
                dna["bank"],

            "suspicious_url":
                dna["suspicious_url"]
        },

        "scam_dna_labels": {

            "urgency":
                localized[
                    "urgency"
                ],

            "threat":
                localized[
                    "threat"
                ],

            "otp":
                localized[
                    "otp"
                ],

            "bank":
                localized[
                    "bank"
                ],

            "suspicious_url":
                localized[
                    "suspicious_url"
                ]
        },

        "memory":
            memory
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {

        "name":
            "AI Scam Shield",

        "status":
            "online",

        "hindsight": {

            "installed":
                True,

            "client":
                "Hindsight",

            "ready":
                HINDSIGHT_READY,

            "bank_id":
                HINDSIGHT_BANK_ID,

            "error":
                HINDSIGHT_ERROR
        },

        "endpoints": [

            "/",

            "/health",

            "/analyze",

            "/scan-screenshot"
        ]
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {

        "status":
            "ok",

        "hindsight_ready":
            HINDSIGHT_READY,

        "hindsight_bank":
            HINDSIGHT_BANK_ID,

        "hindsight_error":
            HINDSIGHT_ERROR
    }


# ============================================================
# ANALYZE
# ============================================================

@app.post("/analyze")
def analyze_endpoint(
    payload: Dict[str, Any]
):

    message = str(
        payload.get(
            "message",
            ""
        )
    ).strip()

    if not message:

        return {
            "error":
                "Message is required."
        }

    return analyze_scam(
        message
    )


# ============================================================
# SCREENSHOT OCR
# ============================================================

@app.post("/scan-screenshot")
async def scan_screenshot(
    file: UploadFile = File(...)
):

    try:

        contents = await file.read()

        image = Image.open(
            io.BytesIO(contents)
        )

        extracted_text = pytesseract.image_to_string(
            image
        )

        extracted_text = re.sub(
            r"https?\s*:\s*/\s*/",
            lambda match:
                match.group(0).replace(
                    " ",
                    ""
                ),
            extracted_text
        )

        extracted_text = extracted_text.strip()

        if not extracted_text:

            return {
                "error":
                    "No text could be extracted from the screenshot."
            }

        analysis = analyze_scam(
            extracted_text
        )

        return {

            "extracted_text":
                extracted_text,

            "analysis":
                analysis
        }

    except Exception as error:

        print(
            "Screenshot OCR error:",
            repr(error)
        )

        return {

            "error":
                f"Screenshot processing failed: {str(error)}"
        }


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup_event():

    print("")
    print("======================================")
    print("       AI SCAM SHIELD BACKEND")
    print("======================================")

    print(
        "Hindsight ready:",
        HINDSIGHT_READY
    )

    print(
        "Hindsight bank:",
        HINDSIGHT_BANK_ID
    )

    if HINDSIGHT_ERROR:

        print(
            "Hindsight error:",
            HINDSIGHT_ERROR
        )

    print("======================================")
    print("")