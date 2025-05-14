import prodigy
from prodigy.components.db import connect
from prodigy.components.preprocess import add_tokens
import spacy
import html
import re
# the Numerical Labels we are using
NUMERICAL_LABELS = ["CARDINAL", "MONEY", "PERCENT", "QUANTITY", "TIME", "DATE", "ORDINAL"]

@prodigy.recipe("numerical_relations", dataset=prodigy.core.Arg(help="Dataset to save annotations."))
def numerical_relations(dataset: str):
    nlp = spacy.blank("en")
    db = connect()
    examples = db.get_dataset("NER_Annotated_Person1")

    stream = []

    def highlight_claim(text):
        # Used to highlight the text in the claim
        match = re.search(r"(Claim:\s*)(.+?)(\s*Document:)", text, re.IGNORECASE | re.DOTALL)
        if match:
            before = html.escape(match.group(1))
            claim = match.group(2)  
            after = html.escape(match.group(3))
            highlighted = f"{before}<span style='background-color: #d0ebff'>{claim}</span>{after}"
            return text.replace(match.group(0), highlighted)
        else:
            return html.escape(text)

    def highlight_numericals(text, spans):
        spans = sorted(spans, key=lambda s: s["start"])
        result = ""
        last_end = 0
        for s in spans:
            result += html.escape(text[last_end:s["start"]])
            result += f"<mark style='background-color: #ffcc80'>{html.escape(text[s['start']:s['end']])}</mark>"
            last_end = s["end"]
        result += html.escape(text[last_end:])
        return result

    for eg in examples:
        text = eg["text"]
        spans = eg.get("spans", [])
        tokens = eg.get("tokens", [])

        numerical_spans = [s for s in spans if s["label"] in NUMERICAL_LABELS]

        numerical_tokens = [
            t for t in tokens
            if any(s["start"] <= t["start"] < s["end"] for s in numerical_spans)
        ]

        # Generate collapsible HTML
        highlighted_text = highlight_numericals(text, numerical_spans)
        combined_html = highlight_claim(highlighted_text)

        html_block = f"""
            <details style="margin-top:10px;">
                <summary><strong>Show Full Context</strong></summary>
                <div style='white-space: pre-wrap; font-family: monospace; font-size: 14px; padding: 12px; border-top: 1px solid #ddd; background: #f9f9f9;'>
                    {combined_html}
                </div>
            </details>
        """

        task = {
            "text": text,
            "tokens": numerical_tokens,
            "spans": numerical_spans,
            "relations": [],
            "_input_hash": eg.get("_input_hash"),
            "html": html_block
        }

        task = list(add_tokens(nlp, [task]))[0]
        stream.append(task)

    return {
        "dataset": dataset,
        "view_id": "blocks",
        "stream": stream,
        "config": {
            "blocks": [
                {"view_id": "relations"},
                {"view_id": "html"},
                {"view_id": "text_input"}
            ],
            "labels": ["MATCHES", "REFERS TO", "INCONSISTENT"],
            "relations_span_labels": NUMERICAL_LABELS
        }
    }
