files = [
    "data/processed/NER_annotated/Ner_Person1.json",
    "data/processed/NER_annotated/Ner_Person2.json",
    "data/processed/NER_annotated/Ner_Person3.json"
]



import json
from collections import defaultdict, Counter

def load_annotations(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def annotation_key(span):
    return (span["start"], span["end"], span["label"])

def merge_annotations(files, output_path):
    datasets = [load_annotations(f) for f in files]

    # Create dict: text -> doc
    maps = [{doc["text"]: doc for doc in dataset} for dataset in datasets]

    # Find common texts in all three
    common_texts = set.intersection(*(set(m.keys()) for m in maps))

    merged = []
    for text in common_texts:
        docs = [m[text] for m in maps]
        merged_spans = defaultdict(int)

        for doc in docs:
            for span in doc.get("spans", []):
                merged_spans[annotation_key(span)] += 1

        final_spans = [
            {
                "start": k[0],
                "end": k[1],
                "label": k[2],
                "text": text[k[0]:k[1]]
            }
            for k, count in merged_spans.items() if count >= 2
        ]

        merged_doc = docs[0].copy()
        merged_doc["spans"] = final_spans
        merged.append(merged_doc)

        

    with open(output_path, "w", encoding="utf-8") as f:
        for doc in merged:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print(f"Merged {len(merged)} documents written to {output_path}")

# Example usage
if __name__ == "__main__":

    output = "merged_output.jsonl"
    merge_annotations(files, output)


