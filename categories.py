"""Category taxonomy and validation helpers for Indonesian app labeling."""

CATEGORIES = {
    "FIN_LOAN_MICRO_CASH": ("Finance", "Loan", "Microloan / Cash Loan"),
    "FIN_LOAN_P2P": ("Finance", "Loan", "Peer-to-Peer Lending"),
    "FIN_LOAN_BNPL": ("Finance", "Loan", "Installment / BNPL"),
    "FIN_LOAN_SME": ("Finance", "Loan", "Business / SME Loan"),
    "FIN_LOAN_COLLATERAL": ("Finance", "Loan", "Secured / Collateral Loan"),
    "FIN_LOAN_MARKETPLACE": ("Finance", "Loan", "Credit Matching / Loan Marketplace"),
    "FIN_CREDIT_SCORE": ("Finance", "Credit Service", "Credit Score / Credit Report"),
    "FIN_BANK_DIGITAL": ("Finance", "Banking", "Digital Bank"),
    "FIN_BANK_TRADITIONAL": ("Finance", "Banking", "Traditional Bank"),
    "FIN_PAYMENT_EWALLET": ("Finance", "Payment", "E-wallet"),
    "FIN_PAYMENT_SERVICE": ("Finance", "Payment", "Payment Service"),
    "FIN_TRANSFER_REMITTANCE": ("Finance", "Money Transfer", "Remittance / Transfer"),
    "FIN_INVEST_STOCK_FUND": ("Finance", "Investment", "Stock / Fund"),
    "FIN_INVEST_CRYPTO": ("Finance", "Investment", "Cryptocurrency"),
    "FIN_INVEST_WEALTH": ("Finance", "Investment", "Wealth Management"),
    "FIN_INSURANCE_SERVICE": ("Finance", "Insurance", "Insurance Service"),
    "FIN_PF_BUDGETING": ("Finance", "Personal Finance", "Budgeting / Accounting"),
    "FIN_TAX_SERVICE": ("Finance", "Tax", "Tax Service"),
    "CON_ECOM_MARKETPLACE": ("Consumption", "E-commerce", "Marketplace"),
    "CON_ECOM_BRAND_STORE": ("Consumption", "E-commerce", "Brand Store"),
    "CON_ECOM_SECOND_HAND": ("Consumption", "E-commerce", "Second-hand Marketplace"),
    "CON_ECOM_DEALS": ("Consumption", "E-commerce", "Group Buying / Deals"),
    "CON_LOCAL_FOOD_DELIVERY": ("Consumption", "Local Service", "Food Delivery"),
    "CON_LOCAL_GROCERY": ("Consumption", "Local Service", "Grocery / Supermarket"),
    "CON_LOCAL_HOME_SERVICE": ("Consumption", "Local Service", "Home Service"),
    "CON_TICKET_MOVIE_EVENT": ("Consumption", "Ticketing", "Movie / Event Ticket"),
    "CON_TRAVEL_BOOKING": ("Consumption", "Travel", "Hotel / Flight Booking"),
    "CON_RESTAURANT_REVIEW": ("Consumption", "Restaurant", "Restaurant Review / Reservation"),
    "SOC_MSG_IM": ("Social", "Messaging", "Instant Messaging"),
    "SOC_NETWORK_GENERAL": ("Social", "Social Network", "General Social"),
    "SOC_COMMUNITY_IMAGE_TEXT": ("Social", "Content Community", "Image / Text Community"),
    "SOC_COMMUNITY_VIDEO": ("Social", "Content Community", "Video Community"),
    "SOC_DATING_MATCH": ("Social", "Dating", "Dating / Matchmaking"),
    "SOC_ANON_CHAT": ("Social", "Anonymous Social", "Anonymous Chat"),
    "SOC_LIVE_VOICE_VIDEO": ("Social", "Live Social", "Voice / Video Chat"),
    "COM_PHONE_SMS": ("Communication", "Phone / SMS", "Caller / SMS"),
    "COM_EMAIL_CLIENT": ("Communication", "Email", "Email Client"),
    "COM_CONTACT_MANAGER": ("Communication", "Contacts", "Contact Manager"),
    "ENT_VIDEO_LONG": ("Entertainment", "Video", "Long Video"),
    "ENT_VIDEO_SHORT": ("Entertainment", "Video", "Short Video"),
    "ENT_MUSIC_STREAMING": ("Entertainment", "Music", "Music Streaming"),
    "ENT_LIVE_PLATFORM": ("Entertainment", "Live Streaming", "Live Platform"),
    "ENT_READING_NOVEL_COMICS": ("Entertainment", "Reading", "Novel / Comics"),
    "ENT_IMAGE_WALLPAPER_GALLERY": ("Entertainment", "Image", "Wallpaper / Gallery"),
    "ENT_MEDIA_PLAYER": ("Entertainment", "Media Tool", "Video / Music Player"),
    "ENT_AUDIO_RADIO_PODCAST": ("Entertainment", "Audio", "Radio / Podcast"),
    "GAME_CASUAL_PUZZLE": ("Games", "Casual", "Casual / Puzzle"),
    "GAME_ACTION": ("Games", "Action", "Action Game"),
    "GAME_FPS": ("Games", "Competitive", "Shooting / FPS"),
    "GAME_MOBA": ("Games", "Competitive", "MOBA"),
    "GAME_RPG": ("Games", "Role Playing", "RPG"),
    "GAME_STRATEGY": ("Games", "Strategy", "Strategy Game"),
    "GAME_CARD_BOARD": ("Games", "Card / Board", "Card / Board Game"),
    "GAME_SPORTS": ("Games", "Sports", "Sports Game"),
    "GAME_KIDS": ("Games", "Kids", "Kids Game"),
    "GAME_CASINO_SIM": ("Games", "Casino", "Simulated Casino Game"),
    "GAME_REWARD_P2E": ("Games", "Reward Game", "Play-to-Earn Game"),
    "TOOL_SYSTEM_CLEANER": ("Tools", "System", "Cleaner / Booster"),
    "TOOL_SYSTEM_FILE_MANAGER": ("Tools", "System", "File Manager"),
    "TOOL_SECURITY_ANTIVIRUS": ("Tools", "Security", "Antivirus / Security"),
    "TOOL_PRIVACY_VPN": ("Tools", "Privacy", "VPN / Proxy"),
    "TOOL_PRIVACY_APP_LOCK": ("Tools", "Privacy", "App Lock / Privacy"),
    "TOOL_INPUT_KEYBOARD": ("Tools", "Input", "Keyboard / IME"),
    "TOOL_BROWSER": ("Tools", "Browser", "Web Browser"),
    "TOOL_DOWNLOADER": ("Tools", "Downloader", "Download Manager"),
    "TOOL_TRANSLATOR": ("Tools", "Translation", "Translator / Dictionary"),
    "TOOL_AI_CHATBOT": ("Tools", "AI", "AI Assistant / Chatbot"),
    "TOOL_CAMERA_EDITOR": ("Tools", "Camera", "Camera / Photo Editor"),
    "TOOL_SCANNER": ("Tools", "Scanner", "QR / Document Scanner"),
    "TOOL_CALCULATOR": ("Tools", "Calculator", "Calculator / Converter"),
    "TOOL_CLOCK": ("Tools", "Clock", "Alarm / Timer"),
    "TOOL_WEATHER": ("Tools", "Utility", "Weather Tool"),
    "LIFE_WEATHER": ("Lifestyle", "Weather", "Weather Forecast"),
    "LIFE_REAL_ESTATE": ("Lifestyle", "Real Estate", "Rental / Property"),
    "LIFE_AUTO": ("Lifestyle", "Auto", "Car Service"),
    "LIFE_BEAUTY": ("Lifestyle", "Beauty", "Beauty / Skincare"),
    "LIFE_PET": ("Lifestyle", "Pet", "Pet Service"),
    "LIFE_RELIGION": ("Lifestyle", "Religion", "Religion / Prayer"),
    "LIFE_HOROSCOPE": ("Lifestyle", "Horoscope", "Astrology / Fortune"),
    "LIFE_WEDDING": ("Lifestyle", "Wedding", "Wedding Service"),
    "LIFE_PARENTING": ("Lifestyle", "Parenting", "Parenting / Baby Care"),
    "MOB_RIDE_HAILING": ("Mobility", "Ride Hailing", "Ride Hailing"),
    "MOB_MAP_NAV": ("Mobility", "Maps", "Map / Navigation"),
    "MOB_PUBLIC_TRANSIT": ("Mobility", "Public Transit", "Bus / Metro"),
    "MOB_LOGISTICS_COURIER": ("Mobility", "Logistics", "Delivery / Courier"),
    "MOB_DRIVER_PARTNER": ("Mobility", "Driver / Courier", "Driver / Delivery Partner"),
    "MOB_PARKING": ("Mobility", "Parking", "Parking Service"),
    "MOB_RENTAL": ("Mobility", "Rental", "Car / Bike Rental"),
    "EDU_LANGUAGE": ("Education", "Language Learning", "English / Foreign Language"),
    "EDU_ONLINE_COURSE": ("Education", "Online Course", "E-learning Platform"),
    "EDU_EXAM_PREP": ("Education", "Exam Prep", "Test Preparation"),
    "EDU_KIDS": ("Education", "Kids Education", "Early Learning"),
    "EDU_SCHOOL_TOOL": ("Education", "School Tool", "Homework / Campus"),
    "EDU_MATERIAL": ("Education", "Learning Material", "Book / Knowledge"),
    "EDU_TUTORING": ("Education", "Tutoring", "Online Tutor"),
    "PROD_OFFICE_DOC": ("Productivity", "Office", "Document / Spreadsheet"),
    "PROD_CLOUD_DRIVE": ("Productivity", "Cloud Storage", "Cloud Drive"),
    "PROD_NOTES_TODO": ("Productivity", "Notes", "Note / To-do"),
    "PROD_VIDEO_MEETING": ("Productivity", "Collaboration", "Video Meeting"),
    "PROD_JOB_SEARCH": ("Productivity", "Job", "Job Search / Recruitment"),
    "PROD_BUSINESS_MERCHANT": ("Productivity", "Business Tool", "Merchant Tool"),
    "PROD_DEV_TOOL": ("Productivity", "Developer Tool", "Coding / Dev Tool"),
    "PROD_CALENDAR": ("Productivity", "Calendar", "Calendar / Schedule"),
    "PROD_PROJECT_MGMT": ("Productivity", "Project Management", "Project / Team Management"),
    "HEALTH_FITNESS": ("Health", "Fitness", "Workout / Exercise"),
    "HEALTH_MEDICAL": ("Health", "Medical", "Telemedicine / Hospital"),
    "HEALTH_PHARMACY": ("Health", "Pharmacy", "Medicine / Pharmacy"),
    "HEALTH_WOMEN": ("Health", "Women Health", "Period / Pregnancy"),
    "HEALTH_MENTAL": ("Health", "Mental Health", "Meditation / Counseling"),
    "HEALTH_DIET": ("Health", "Diet", "Nutrition / Weight Loss"),
    "HEALTH_DEVICE": ("Health", "Device", "Wearable / Health Tracker"),
    "NEWS_GENERAL": ("News", "General News", "News App"),
    "NEWS_FINANCE": ("News", "Finance News", "Financial News"),
    "NEWS_SPORTS": ("News", "Sports News", "Sports News"),
    "NEWS_LOCAL": ("News", "Local News", "Local Information"),
    "NEWS_AGGREGATOR": ("News", "Content Aggregator", "Feed / Aggregator"),
    "NEWS_GOV_INFO": ("News", "Government Info", "Public Service Info"),
    "RISK_GAMBLING_SPORTS": ("Special Risk", "Gambling", "Sports Betting"),
    "RISK_GAMBLING_CASINO": ("Special Risk", "Gambling", "Casino / Slots"),
    "RISK_REWARD_AD": ("Special Risk", "Reward Earning", "Ad Reward"),
    "RISK_REWARD_CASH": ("Special Risk", "Reward Earning", "Cash Reward App"),
    "RISK_LOAN_GRAY_BROKER": ("Special Risk", "Loan Gray Market", "Loan Broker / Credit Hack"),
    "RISK_PRIVACY_VPN": ("Special Risk", "Privacy Evasion", "VPN / Proxy"),
    "RISK_DEVICE_FAKE_GPS": ("Special Risk", "Device Evasion", "Fake GPS / Location Spoofing"),
    "RISK_DEVICE_CLONER": ("Special Risk", "Device Evasion", "App Cloner / Multi-account"),
    "RISK_DEVICE_EMULATOR": ("Special Risk", "Device Evasion", "Emulator / Device Spoofing"),
    "RISK_ADULT_DATING": ("Special Risk", "Adult / Dating", "Adult Dating"),
    "RISK_ADULT_CONTENT": ("Special Risk", "Adult / Content", "Adult Content"),
    "RISK_DEBT_COLLECTION": ("Special Risk", "Debt Collection", "Collection / Debt Management"),
    "RISK_SUSPICIOUS_FRAUD": ("Special Risk", "Suspicious", "Scam / Fraud Suspected"),
    "RISK_HIGH_INTEREST_LOAN": ("Special Risk", "High-risk Finance", "High-interest Loan"),
    "GOV_IDENTITY": ("Government", "Identity", "Digital ID / Identity Service"),
    "GOV_TAX_INVOICE": ("Government", "Tax", "Tax / Invoice Service"),
    "GOV_SOCIAL_SECURITY": ("Government", "Social Security", "Social Security Service"),
    "GOV_PUBLIC_SERVICE": ("Government", "Public Service", "Government Service"),
    "GOV_LEGAL_POLICE": ("Government", "Legal / Police", "Legal / Police Service"),
    "OTH_UNKNOWN": ("Other", "Unknown", "Insufficient Information"),
    "OTH_SYSTEM_APP": ("Other", "System App", "Pre-installed App"),
    "OTH_SUPER_APP": ("Other", "Multi-purpose", "Super App"),
    "OTH_OTHERS": ("Other", "Others", "Others"),
    "OTH_TEST_DEMO": ("Other", "Test / Demo", "Test App"),
}


def category_path(parts):
    return " \u2192 ".join(parts)


CATEGORY_PATH_TO_CODE = {category_path(parts): code for code, parts in CATEGORIES.items()}


HIGH_RISK_PREFIXES = {
    ("Finance", "Loan"),
    ("Finance", "Credit Service"),
    ("Special Risk", "Gambling"),
    ("Special Risk", "Reward Earning"),
    ("Special Risk", "Loan Gray Market"),
    ("Special Risk", "Device Evasion"),
    ("Special Risk", "Debt Collection"),
    ("Special Risk", "High-risk Finance"),
}

MEDIUM_RISK_PREFIXES = {
    ("Finance", "Payment"),
    ("Finance", "Banking"),
    ("Finance", "Investment"),
    ("Finance", "Insurance"),
    ("Social", "Dating"),
    ("Productivity", "Job"),
    ("Consumption", "E-commerce"),
    ("Tools", "Privacy"),
    ("Government", "Identity"),
}


def expected_risk(level1, level2):
    pair = (level1, level2)
    if pair in HIGH_RISK_PREFIXES:
        return "High"
    if pair in MEDIUM_RISK_PREFIXES:
        return "Medium"
    return "Low"


def normalize_record(record):
    code = record.get("category_code")
    path = record.get("category_path")

    if code in CATEGORIES:
        parts = CATEGORIES[code]
    elif path in CATEGORY_PATH_TO_CODE:
        code = CATEGORY_PATH_TO_CODE[path]
        parts = CATEGORIES[code]
    else:
        code = "OTH_UNKNOWN"
        parts = CATEGORIES[code]

    level1, level2, level3 = parts
    record["category_code"] = code
    record["level1"] = level1
    record["level2"] = level2
    record["level3"] = level3
    record["category_path"] = category_path(parts)
    record["risk_relevance"] = expected_risk(level1, level2)

    if code == "OTH_UNKNOWN":
        record["is_description_sufficient"] = False
        record["risk_relevance"] = "Low"

    try:
        confidence = float(record.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    record["confidence"] = min(1.0, max(0.0, confidence))

    return record


def taxonomy_text():
    lines = []
    for code, parts in CATEGORIES.items():
        lines.append(f"- {code}: {category_path(parts)}")
    return "\n".join(lines)
