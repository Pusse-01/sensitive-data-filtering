# from nightfall import Confidence, RedactionConfig, DetectionRule, Detector, Nightfall
import os
import presidio_analyzer
from presidio_analyzer import AnalyzerEngine, LocalRecognizer, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
import re
import spacy


def redact_money(text):
    # print(text)
    # Regular expression pattern to match money amounts
    # pattern = r'(?i)\b(?:\d+(?:[.,]\d+)?\s*(?:million|billion)?\s*(?:dollars|euros|rupees|rs|lkr|rs.)|(?:dollars|euros|rupees|rs|lkr|rs.)\s*\d+(?:[.,]\d+)?)\b'
    pattern = r'(?i)(?:\$?\s*)?\b(?:\d+(?:[.,]\d+)?\s*(?:mn | bn | million|billion)?\s*(?:dollars|euros|rupees|rs|lkr|rs.)|(?:dollars|euros|rupees|rs|lkr|rs.)\s*\d+(?:[.,]\d+)?)\b'

    # Find all matches of the pattern in the text
    matches = re.findall(pattern, text)
    # print(matches)
    # Redact the matches in the text
    redacted_text = text
    for match in matches:
        redacted_text = redacted_text.replace(match, '[MONEY]')

    return redacted_text

class MyFinancialRecognizer(LocalRecognizer):
    def __init__(self):
        self.supported_entities = ["MONEY", "PERCENT"]
        self.supported_language = "en"
        self.nlp = None
        self.is_loaded = False
        self._id = "custom_recognizer"
        self.name = "My Financial Recognizer"
        self.context = ''

    def load(self):
        # Load the spaCy model for English
        self.nlp = spacy.load("en_core_web_sm")

    def analyze(self, text, entities, nlp_artifacts):
        if not self.nlp:
            self.load()

        # Process the text using spaCy
        doc = self.nlp(text)

        results = []

        # Extract money amounts
        for ent in doc.ents:
            if ent.label_ == "MONEY":
                results.append(
                    RecognizerResult(
                        entity_type="MONEY",
                        start=ent.start_char,
                        end=ent.end_char,
                        score=1.0,
                    )
                )

            # Extract percentages
            elif ent.label_ == "PERCENT":
                # Find the number preceding the percentage sign
                prev_token = doc[ent.start - 1]
                if prev_token.like_num:
                    number = prev_token.text
                    percent = ent.text
                    combined_entity = number + percent
                    results.append(
                        RecognizerResult(
                            entity_type="PERCENT",
                            start=prev_token.idx,
                            end=ent.end_char,
                            score=1.0,  # Adjust the confidence score as needed
                        ))

        return results

import re

def replace_race_tags(text):
    ethnicity_keywords = {
        'African': ['akan', 'amhara', 'ashanti', 'bantu', 'berber', 'igbo', 'khoisan', 'somali', 'yoruba', 'zulu'],
        'Asian': ['bengali', 'chinese', 'filipino', 'gujarati', 'japanese', 'korean', 'malay', 'punjabi', 'tamil', 'vietnamese'],
        'European': ['english', 'french', 'german', 'greek', 'irish', 'italian', 'polish', 'russian', 'spanish', 'swedish'],
        'Indigenous': ['aboriginal', 'inuit', 'maori', 'native american', 'sami', 'torres strait islander', 'xhosa'],
        'Middle Eastern': ['arab', 'assyrian', 'iranian', 'jewish', 'kurdish', 'pashtun', 'persian', 'turkish', 'yazidi'],
        'Native American': ['apache', 'cherokee', 'choctaw', 'hopi', 'inca', 'iroquois', 'navajo', 'sioux', 'yaqui'],
        'Pacific Islander': ['fijian', 'hawaiian', 'maori', 'papua new guinean', 'polynesian', 'samoan', 'tongan', 'tuvaluan'],
        'South American': ['andean', 'guarani', 'inca', 'mapuche', 'quechua', 'wayuu', 'yanomami']
    }

    for ethnicity, keywords in ethnicity_keywords.items():
        for keyword in keywords:
            pattern = r'\b{}\b'.format(keyword)
            text = re.sub(pattern, '[RACE]', text, flags=re.IGNORECASE)

    return text



def replace_organization_names(text):
    # Load the English language model in spaCy
    nlp = spacy.load('en_core_web_sm')
    
    # Process the input text
    doc = nlp(text)
    
    # Iterate over the named entities in the document
    for ent in doc.ents:
        if ent.label_ == 'ORG':
            # Replace organization names with [ORG]
            text = text.replace(ent.text, '[ORG]')
    
    return text

def replace_addresses_with_tag(text):
    # Load the English language model in spaCy
    nlp = spacy.load("en_core_web_sm")
    
    # Define a regular expression pattern to match addresses
    address_pattern = r"\d+\s+\w+\s+\w+|P\.?O\.?\s+Box\s+\d+"
    
    # Apply spaCy's NLP pipeline to the input text
    doc = nlp(text)
    
    # Find addresses using regular expressions and replace them with [ADDRESS] tag
    modified_text = re.sub(address_pattern, "[ADDRESS]", doc.text)
    
    return modified_text

def detect_sexual_orientation(text):
    # Define a list of words related to sexual orientation
    sexual_orientation_words = ['gay', 'lesbian', 'homosexual', 'heterosexual', 'bisexual', 'pansexual', 'queer', 'transgender']
    
    # Create a regular expression pattern to match the words (case-insensitive)
    pattern = re.compile(r'\b(?:' + '|'.join(sexual_orientation_words) + r')\b', re.IGNORECASE)
    
    # Replace the words with [SO]
    modified_text = pattern.sub('[SO]', text)
    
    return modified_text

def anonymize_user_credentials(text): 
    text = re.sub(r"(username: | \"username\":)\s*\S+", r"\1 [USERNAME]", text, flags=re.I) 
    text = re.sub(r"(password: | \"password\":)\s*\S+", r"\1 [PASSWORD]", text, flags=re.I) 
    return text 

def scan_text_spacy(text):
    # Set up the analyzer engine and registry
    analyzer = AnalyzerEngine()
    registry = analyzer.registry

    # Create an instance of your custom recognizer
    my_recognizer = MyFinancialRecognizer()

    # Add your custom recognizer to the registry
    registry.add_recognizer(my_recognizer)

    # Call the analyzer to get results
    results = analyzer.analyze(
        text=text,
        entities=[
                            "PHONE_NUMBER",
                            # "US_DRIVER_LICENSE",
                            "US_PASSPORT",
                            "LOCATION",
                            "CREDIT_CARD",
                            # "CRYPTO",
                            # "UK_NHS",
                            # "US_SSN",
                            "US_BANK_NUMBER",
                            "EMAIL_ADDRESS",
                            "DATE_TIME",
                            "IP_ADDRESS",
                            "PERSON",
                            # "IBAN_CODE",
                            "NRP",
                            # "US_ITIN",
                            # "MEDICAL_LICENSE",
                            "URL"
                            ],
        language="en",
    )
    print(results)

    # Use the AnonymizerEngine for anonymization
    anonymizer = AnonymizerEngine()
    anonymized_text = anonymizer.anonymize(text=text, analyzer_results=results)
    anonymized_text.text = redact_money(anonymized_text.text)
    anonymized_text.text = replace_organization_names(anonymized_text.text)
    anonymized_text.text = replace_race_tags(anonymized_text.text)
    anonymized_text.text = replace_addresses_with_tag(anonymized_text.text)
    anonymized_text.text = detect_sexual_orientation(anonymized_text.text)
    anonymized_text.text = anonymize_user_credentials(anonymized_text.text) 
    return anonymized_text

