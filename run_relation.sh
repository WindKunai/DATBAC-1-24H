#!/bin/bash

# Name of the conda environment
VEnv="Prodigy_Env"

# Commands to run in each screen session
command="PRODIGY_HOST=0.0.0.0 PRODIGY_PORT=8084 python -m prodigy numerical_relations Numeric_Relations_DB -F code/Recipe/Relational_Recipe.py"
screen_name="prodigy_Relation"


echo "Starting screen: $screen_name"
screen -dmS "$screen_name" bash -c "
    source activate $VEnv && \
    ${command}; exec bash
    "

echo "Screen started and detached. Use 'screen -r <name>' to attach."
