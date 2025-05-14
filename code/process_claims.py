### Given By Vinay, but modified


"""Module to load, process, and save tagged claims data."""

import spacy
import json
from word2number import w2n
from spacy.cli import download
from spacy.language import Language
from typing import Set, Any, Dict, List, Optional, Tuple


def load_json_data(path: str) -> List[Dict[str, Any]]:
    """Load JSON data from a file and return it as a list of dictionaries."""
    with open(path, "r") as file:
        data = json.load(file)
    return data


def url_true_claim_statistical(data: list, cond: bool) -> dict:
    """Extract claims.

    Need to be statistical with label True and return a dictionary of URL (used
    as ID) and the claim.
    """
    url_and_claim = {}
    for item in data:
        if cond is True and (
            item.get("label") == "True"
        ):
            url_and_claim[item.get("url")] = item.get("claim")
        elif cond is False and (
            item.get("label") == "False"
        ):
            url_and_claim[item.get("url")] = item.get("claim")
        elif cond == "Half True/False" and (
            item.get("label") == "Half True/False"
        ):
            url_and_claim[item.get("url")] = item.get("claim")
    return url_and_claim


def get_number_words_set() -> set:
    """Return a set of valid number words."""
    return set(
        """
        zero one two three four five six seven eight nine ten eleven twelve
        thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty
        thirty forty fifty sixty seventy eighty ninety hundred thousand
        million billion trillion point half quarter
    """.split()
    )


def get_multipliers() -> Dict[str, int]:
    """Return a dictionary of multiplier words and their values."""
    return {
        "thousand": 1000,
        "million": 1000000,
        "billion": 1000000000,
        "trillion": 1000000000000,
    }


def is_number_word(word: str) -> bool:
    """Check if a word is a valid number word."""
    word = word.lower().replace("-", "").strip(".,")
    if word in get_number_words_set():
        return True
    try:
        float(word.replace(",", ""))
        return True
    except ValueError:
        return False


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


def process_claim(claim: str) -> str:
    """Processes claim by converting number words into numerical digits.

    This function scans through the input claim and identifies sequences of
    words that represent numbers. It converts these number words into
    their corresponding numerical digits. The function handles number phrases
    up to four words in length and accounts for multipliers
    like 'thousand' or 'million'.

    Args:
        claim (str): The textual claim containing words and
        number words.

    Returns:
        str: The processed claim with number words converted
        into digits.

    Example:
        >>> process_claim("I have one hundred twenty three apples.")
        'I have 123 apples.'
    """
    words = claim.split()  # Split the claim into words.
    normalized_words = []
    i = 0

    while i < len(words):
        max_length = min(
            4, len(words) - i
        )  # Maximum number of words to consider.
        converted = False

        for length in range(max_length, 0, -1):  # Check longer phrases first.
            phrase_words = words[i : i + length]
            if all(
                is_number_word(word.strip(".,")) for word in phrase_words
            ) or (
                len(phrase_words) == 2
                and is_number_word(phrase_words[0].strip("$.,"))
                and phrase_words[1].lower() in get_multipliers()
            ):
                phrase = " ".join(phrase_words)
                number = convert_phrase(phrase)
                if number is not None:
                    normalized_words.append(number)
                    i += length  # Skip the processed words.
                    converted = True
                    break

        if not converted:  # If no conversion was done, keep the original word.
            normalized_words.append(words[i])
            i += 1

    return " ".join(normalized_words)


def normalize_w2n(url_and_claim: Dict[str, str]) -> Dict[str, str]:
    """Converts number words to numbers using the word2number library."""
    return {url: process_claim(claim) for url, claim in url_and_claim.items()}


def is_model_available(model_name: str) -> bool:
    """Indicate whether a spaCy model is available.

    Args:
        model_name (str): Name of the spaCy model.

    Returns:
        bool: True if the model is available, False otherwise.
    """
    try:
        spacy.load(model_name)
        return True
    except Exception:
        return False


def initialize_spacy() -> Optional[Language]:
    """Load the spaCy model and return it.

    Returns:
        Language: The spaCy language model.
    """
    model_name = "en_core_web_trf"
    if not is_model_available(model_name):
        download(model_name)
    try:
        return spacy.load(model_name)
    except OSError as e:
        print(f"Error loading spaCy model: {e}")
        return None


def get_target_entities() -> Set[str]:
    """Return set of entity types we want to classify."""
    return {
        "CARDINAL",
        "MONEY",
        "PERCENT",
        "QUANTITY",
        "TIME",
        "DATE",
        "IMPORTANT",
        "ORDINAL",
    }


def is_token_mergeable(token, number_words_set: set) -> bool:
    """Determine if token should be part of number merge."""
    return (
        token.like_num
        or token.lower_ in number_words_set
        or token.text in "$£€¥"
    )


def is_token_part_of_merge(token, number_words_set: set) -> bool:
    """Check if next token should be included in merge."""
    return (
        token.like_num
        or token.lower_ in number_words_set
        or token.text.lower() in ["point", ".", ",", "-"]
    )


def find_spans_to_merge(doc, number_words_set: set) -> list:
    """Find all spans of tokens that should be merged."""
    spans_to_merge = []
    i = 0
    while i < len(doc):
        if is_token_mergeable(doc[i], number_words_set):
            start = i
            while (i + 1 < len(doc)) and is_token_part_of_merge(
                doc[i + 1], number_words_set
            ):
                i += 1
            spans_to_merge.append(doc[start : i + 1])
        i += 1
    return spans_to_merge


def extract_entity_info(ent) -> dict:
    """Extract relevant information from an entity."""
    return {
        "text": ent.text,
        "label": ent.label_,
        "start_char": ent.start_char,
        "end_char": ent.end_char,
    }


def process_single_claim(
    doc: spacy.tokens.Doc, number_words_set: set, target_entities: set
) -> dict:
    """Process a single claim and return token information."""
    # Initialize lists to store tokens and annotations
    tokens = [token.text for token in doc]
    annotations = ["O"] * len(tokens)

    # Process named entities
    for ent in doc.ents:
        if ent.label_ in target_entities:
            for idx in range(ent.start, ent.end):
                annotations[idx] = ent.label_

    # Extract entity information
    entities = [
        extract_entity_info(ent)
        for ent in doc.ents
        if ent.label_ in target_entities
    ]

    return {
        "claim": doc.text,
        "tokens": tokens,
        "ner_tags": annotations,
        "entities": entities,
    }


def classify_entities(
    nlp: Language, input_dict: Dict[str, str]
) -> Dict[str, Dict[str, Any]]:
    """Classify entities in claims, return a dictionary of URL-based results."""
    target_entities = get_target_entities()
    number_words_set = get_number_words_set()

    return {
        url_id: process_single_claim(
            nlp(text), number_words_set, target_entities
        )
        for url_id, text in input_dict.items()
    }


def process_data(data: list) -> Tuple[dict, dict]:
    """Extract claims True statistical claims.

    Extracts statistical claims, normalize numbers, classify entities, and
    return the processed data.
    """
    nlp = initialize_spacy()
    false_url_and_claim = url_true_claim_statistical(data, cond=False)
    true_url_and_claim = url_true_claim_statistical(data, cond=True)
    false_normalized_claims = normalize_w2n(false_url_and_claim)
    true_normalized_claims = normalize_w2n(true_url_and_claim)
    false_result_dict = classify_entities(nlp, false_normalized_claims)
    true_result_dict = classify_entities(nlp, true_normalized_claims)
    
    for url, claim in false_url_and_claim.items():
        false_result_dict[url]['doc'] = claim
    for url, claim in true_url_and_claim.items():
        true_result_dict[url]['doc'] = claim

    return false_result_dict, true_result_dict


def main(input_json_path: str, output_json_path1: str, output_json_path2: str):
    """Loads JSON data, processes it, and saves it."""
    data = load_json_data(input_json_path)
    false_result_dict, true_result_dict = process_data(data)
    with open(output_json_path1, "w") as outfile:
        json.dump(false_result_dict, outfile, ensure_ascii=False, indent=4)
    with open(output_json_path2, "w") as outfile:
        json.dump(true_result_dict, outfile, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    # Replace with your input and output file paths
    input_json_path = "data/binary_data/filtered_new_quantemp_claims_10p_Sample1.json"
    output_json_path1 = (
        "data/processed/tagged/new_tagged_claims_10p_Sample_3.json"
    )
    output_json_path2 = (
        "data/processed/tagged/new_tagged_claims_10p_Sample_4.json"
    )
    main(input_json_path, output_json_path1, output_json_path2)
