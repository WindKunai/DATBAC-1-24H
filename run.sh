#!/bin/bash

# Name of the conda environment
VEnv="Prodigy_Env"

# Commands to run in each screen session
declare -A commands=(
    ["prodigy_Person1"]="PRODIGY_HOST=0.0.0.0 PRODIGY_PORT=8081 python -m prodigy NER_annotation NER_Annotated_Person1 data/processed/tagged/spaCy_Results.json -F code/Recipe/Ner_Recipe.py"
    ["prodigy_Person2"]="PRODIGY_HOST=0.0.0.0 PRODIGY_PORT=8082 python -m prodigy NER_annotation NER_Annotated_Person2 data/processed/tagged/spaCy_Results.json -F code/Recipe/Ner_Recipe.py"
    ["prodigy_Person3"]="PRODIGY_HOST=0.0.0.0 PRODIGY_PORT=8083 python -m prodigy NER_annotation NER_Annotated_Person3 data/processed/tagged/spaCy_Results.json -F code/Recipe/Ner_Recipe.py"
)

# Loop through the commands and start each in its own screen session
for screen_name in "${!commands[@]}"; do
    echo "Starting screen: $screen_name"
    screen -dmS "$screen_name" bash -c "
        source activate $VEnv && \
        ${commands[$screen_name]}; exec bash
    "
done

echo "All screens started and detached. Use 'screen -r <name>' to attach."
