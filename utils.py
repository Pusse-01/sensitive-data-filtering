# from nightfall import Confidence, RedactionConfig, DetectionRule, Detector, Nightfall
import os
from presidio_analyzer import AnalyzerEngine, LocalRecognizer, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
import re
import spacy

def redact_money(text):
    # Regular expression pattern to match money amounts
    pattern = r'(?i)\b(?:\d+(?:[.,]\d+)?\s*(?:million|billion)?\s*(?:dollars|euros|rupees|rs|lkr|rs.)|(?:dollars|euros|rupees|rs|lkr|rs.)\s*\d+(?:[.,]\d+)?)\b'

    # Find all matches of the pattern in the text
    matches = re.findall(pattern, text)

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


# def scan_text_spacy(text):
#     # Set up the engine, loads the NLP module (spaCy model by default) 
#     # and other PII recognizers
#     analyzer = AnalyzerEngine()

#     # Call analyzer to get results
#     results = analyzer.analyze(text=text,
#                             entities=[
#                             "PHONE_NUMBER",
#                             # "US_DRIVER_LICENSE",
#                             # "US_PASSPORT",
#                             "LOCATION",
#                             "CREDIT_CARD",
#                             # "CRYPTO",
#                             # "UK_NHS",
#                             # "US_SSN",
#                             "US_BANK_NUMBER",
#                             "EMAIL_ADDRESS",
#                             # "DATE_TIME",
#                             # "IP_ADDRESS",
#                             "PERSON",
#                             # "IBAN_CODE",
#                             "NRP",
#                             # "US_ITIN",
#                             # "MEDICAL_LICENSE",
#                             "URL"
#                             ],
#                             language='en')
#     print(results)

#     # Analyzer results are passed to the AnonymizerEngine for anonymization

#     anonymizer = AnonymizerEngine()

#     anonymized_text = anonymizer.anonymize(text=text,analyzer_results=results)

#     return(anonymized_text)

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
                            # "US_PASSPORT",
                            "LOCATION",
                            "CREDIT_CARD",
                            # "CRYPTO",
                            # "UK_NHS",
                            # "US_SSN",
                            "US_BANK_NUMBER",
                            "EMAIL_ADDRESS",
                            # "DATE_TIME",
                            # "IP_ADDRESS",
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
    return anonymized_text

