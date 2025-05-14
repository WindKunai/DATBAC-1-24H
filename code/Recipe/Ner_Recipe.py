import prodigy
from prodigy.components.preprocess import add_tokens
from prodigy import set_hashes
import json
from pathlib import Path
import spacy




@prodigy.recipe(
    "NER_annotation",
    dataset=prodigy.core.Arg(help="Dataset to save annotations."),
    file_path=prodigy.core.Arg(help="Path to the JSON file with claims and documents.")
)
def NER_annotation(dataset: str, file_path: Path):
    """Annotate named entities and relations in a claim and document."""
    # Load the JSON file
    with open(file_path, 'r', encoding="utf-8") as file:
        data = json.load(file)

    # Initialize spaCy model for tokenization
    nlp = spacy.blank("en")  # Using blank model to add tokens

    # Define numerical labels
    NUMERICAL_LABELS = ["CARDINAL", "MONEY", "PERCENT", "QUANTITY", "TIME", "DATE", "ORDINAL"]

    # Prepare the stream of tasks
    stream = []
    for url, content in data.items():

        # Defining the data and the prefixes
        claim = content['claim']
        claim_entities = content.get('claim_entities', [])
        doc = content['doc']
        doc_entities = content.get('doc_entities', [])
        
        label = content.get('label', '')
        label_prefix = "Label: "

        claim_prefix = "\n\nClaim: "
        doc_prefix = "\n\nDocument: "

        FeedbackInstructions = "\n\nInstructions: Any additional issues or information required please input that in the box bellow"

        # Is essentially the order of the content in the stream
        combined_text = f"{label_prefix}{label}{claim_prefix}{claim}{doc_prefix}{doc}{FeedbackInstructions}"

        # Important, as it keeps track of what extra has been added so that spans are correct
        claim_offset = len(claim_prefix)+len(label_prefix)+len(label)
 
        adjusted_claim_entities = [
            {
                "start": entity["start"] + claim_offset,
                "end": entity["end"] + claim_offset,
                "label": entity["label"],
                "text": claim[entity["start"]:entity["end"]]
            }
            for entity in claim_entities
        ]

        # Caluclating the same but for everything that comes before the document
        doc_offset = len(f"{label_prefix}{label}{claim_prefix}{claim}{doc_prefix}")
        adjusted_doc_entities = [
            {
                "start": entity["start"] + doc_offset,
                "end": entity["end"] + doc_offset,
                "label": entity["label"],
                "text": doc[entity["start"]:entity["end"]]
            }
            for entity in doc_entities
        ]

        # Build the complete list of spans (first claim then document entities)
        spans = adjusted_claim_entities + adjusted_doc_entities

        # Filter numerical spans
        numerical_spans = [span for span in spans if span["label"] in NUMERICAL_LABELS]

        # Creates the annotation task
        task = {
            "text": combined_text,
            "meta": {"url": url},
            "spans": spans,
            "numerical_spans": numerical_spans  # Store filtered numerical spans
        }

        stream.append(task)

    # Uses add_tokens() for proper tokenization (like ner_manual)
    stream = add_tokens(nlp, stream)
    stream = (set_hashes(eg) for eg in stream)

    # Define blocks for UI layout
    blocks = [
        {
                    "view_id": "html",
                    "html": """
<!doctype html>
<html lang="en">
        <h1> NER Annotation </h1>
        <h3>Please label the entities in the claim and document. See <a href='https://docs.google.com/document/d/1klT7cgTs4SqHgH3vAyI03mJZSYZLDvLfHB5eA25JTDg' target="_blank">HERE</a> for more information</p>
        <h3>Please choose the appropriate box if the claim is or is not numerical based. </h3>
</html>


    """
        },        
        {
            "view_id": "choice", 
            "text": None, 
            "options": [  
                {"id": "numerical", "text": "Numerical focused"},
                {"id": "not_numerical", "text": "Not Numerical Focused"}
            ]
        },
        {"view_id": "ner_manual"},
        {"view_id": "text_input"}
    ]

    return {
        "dataset": dataset,
        "view_id": "blocks",  # Combination of the different blocks 
        "stream": stream, 
        "config": {
            "blocks": blocks,
            "labels": ["CARDINAL", "MONEY", "PERCENT", "QUANTITY", "TIME", "DATE", "ORDINAL"],
        }

    }