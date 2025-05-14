import spacy
import re
from spacy.tokenizer import Tokenizer

import json
from typing import List, Set, Optional
from word2number import w2n
from typing import Set, Any, Dict, List, Optional
from process_claims import get_target_entities

# Load the pre-trained spaCy model
nlp = spacy.load('en_core_web_sm')

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)  # regular dict


def convert_phrase(phrase: str) -> Optional[str]:
    """Convert a phrase of words to a formatted number with commas."""
    try:
        words = phrase.lower().split()
        result, has_dollar = handle_currency_and_multiplier(words)

        if result:
            return result

        # Regular conversion for other cases
        num = w2n.word_to_num(phrase)
        formatted = "{:,}".format(num)
        return f"${formatted}" if has_dollar else formatted
    except ValueError:
        return None

def handle_currency_and_multiplier(words: List[str]) -> tuple:
    """Process currency symbols and multipliers in number words."""
    has_dollar = False
    if words[0].startswith("$"):
        words[0] = words[0][1:]
        has_dollar = True

    if len(words) == 2 and words[1] in get_multipliers():
        try:
            base_num = float(words[0].replace(",", ""))
        except ValueError:
            try:
                base_num = w2n.word_to_num(words[0])
            except ValueError:
                return None, has_dollar

        final_num = base_num * get_multipliers()[words[1]]
        formatted = "{:,.0f}".format(final_num)
        return f"${formatted}" if has_dollar else formatted, has_dollar

    return None, False

def get_multipliers() -> Dict[str, int]:
    """Return a dictionary of multiplier words and their values."""
    return {
        "thousand": 1000,
        "million": 1000000,
        "billion": 1000000000,
        "trillion": 1000000000000,
    }

# Tokenize and label text using spaCy
def tokenize_and_label(text):
    nlp.tokenizer = custom_tokenizer(nlp)
    doc = nlp(text)
    tokens = [token.text for token in doc]
    return tokens

def custom_tokenizer(nlp):
    infix_re = re.compile(r'''[.\,\?\:\;\(\)\[\]\{\}]''') 
    return Tokenizer(nlp.vocab, infix_finditer=infix_re.finditer)

# Extract entities from text using spaCy
def extract_entities(text):
    doc = nlp(text)
    entities = []

    for ent in doc.ents:

        if ent.label_ in get_target_entities():
            formatted_value = convert_phrase(ent.text) if ent.label_ in {"MONEY", "CARDINAL", "QUANTITY", "PERCENT"} else None
            
            # Using spaCy's tokenization -> to get the start and end token indices
            start_token = doc[ent.start]
            end_token = doc[ent.end - 1]
            
            entity_entry = {
                "text": formatted_value if formatted_value else ent.text,
                "label": ent.label_,
                "start": start_token.idx,
                "end": end_token.idx + len(end_token)
            }
            entities.append(entity_entry)
    
    return entities
# takes data and adds it to a list in correct format
def process_data(json_data):
    output = []    
    counter = 0
    for entry in json_data:
        counter += 1

        url = entry.get("url", "")
    
        claim = entry.get("claim", "")
        claim_entities = extract_entities(claim)
        
        doc = entry.get("doc", "")
        doc_entities = extract_entities(doc)
        
        label = entry.get("label", "")

        output.append({
            url: {
            "label": label,
            "claim": claim,
            "claim_entities": claim_entities,
            "doc": doc,
            "doc_entities": doc_entities
            }
        })
        print(counter)
        
    return output

# Loads the data
with open('../../../data/binary_data/filtered_quantemp_claims_10p.json', 'r') as file:
    data = json.load(file)

processed_data = process_data(data)
#Allocates where the output is
output_filename = '../../../data/binary_data/241LENGTH.json'
with open(output_filename, 'w') as outfile:
    json.dump(processed_data, outfile, indent=4)

# Verifies output location
print(f"Data has been processed and saved to {output_filename}")
