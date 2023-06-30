from nightfall import Confidence, RedactionConfig, DetectionRule, Detector, Nightfall
import os
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

def scan_text(text):
    # By default, the client reads the API key from the environment variable NIGHTFALL_API_KEY
    nightfall = Nightfall()

    # A rule contains a set of detectors to scan with
    name = Detector(min_confidence=Confidence.POSSIBLE, nightfall_detector="PERSON_NAME", display_name="Name",
                                redaction_config=RedactionConfig(
                                    remove_finding=False, 
                                    substitution_phrase="[name]"))
    email = Detector(min_confidence=Confidence.POSSIBLE, nightfall_detector="EMAIL_ADDRESS", display_name="Email",
                                redaction_config=RedactionConfig(
                                    remove_finding=False, 
                                    substitution_phrase="[email]"))
    phone = Detector(min_confidence=Confidence.POSSIBLE, nightfall_detector="PHONE_NUMBER", display_name="Phone No",
                                redaction_config=RedactionConfig(
                                    remove_finding=False, 
                                    substitution_phrase="[phones]"))
    passwords = Detector(min_confidence=Confidence.POSSIBLE, nightfall_detector="PASSWORD_IN_CODE", display_name="Password",
                                redaction_config=RedactionConfig(
                                    remove_finding=False, 
                                    substitution_phrase="[password]"))
    cc = Detector(min_confidence=Confidence.POSSIBLE, nightfall_detector="CREDIT_CARD_NUMBER", display_name="Credit Card Number",
                                redaction_config=RedactionConfig(
                                    remove_finding=False, 
                                    substitution_phrase="[Credit Card Number]"))
    

    detection_rule = DetectionRule([
                                name, email, phone, passwords,cc])

    findings, redacted_payload = nightfall.scan_text( [text], detection_rules=[detection_rule])
    # If the message has sensitive data, use the redacted version, otherwise use the original message
    print(redacted_payload)
    if redacted_payload[0]:
        message_body = redacted_payload[0]
    else:
        message_body = text
    return message_body

# print(findings)

def scan_text_spacy(text):
    # Set up the engine, loads the NLP module (spaCy model by default) 
    # and other PII recognizers
    analyzer = AnalyzerEngine()

    # Call analyzer to get results
    results = analyzer.analyze(text=text,
                            # entities=["PHONE_NUMBER"],
                            language='en')
    print(results)

    # Analyzer results are passed to the AnonymizerEngine for anonymization

    anonymizer = AnonymizerEngine()

    anonymized_text = anonymizer.anonymize(text=text,analyzer_results=results)

    return(anonymized_text)
