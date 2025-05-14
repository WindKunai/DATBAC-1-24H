# Annotation Tool for Building Datasets for Fact-Checking Machine Learning Models

This repository contains an annotation tool developed for building datasets used in fact-checking machine learning models. The tool helps streamline the annotation process for creating high-quality training data.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- virtualenv

## Installation

Follow these steps to set up the environment and install the necessary dependencies:

1. Clone the repository:
   ```
   git clone https://github.com/WindKunai/DATBAC-1-24H.git
   cd annotation-tool
   ```

2. Create a virtual environment named **Prodigy_Env** (this specific name is REQUIRED - the scripts won't work with any other name):
   ```
   virtualenv Prodigy_Env
   ```

3. Activate the virtual environment:
   
   **On Linux/Mac**:
   ```
   source Prodigy_Env/bin/activate
   ```
   
   **On Windows**:
   ```
   Prodigy_Env\Scripts\activate
   ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Tool

The annotation process consists of two sequential steps that must be performed in the correct order:

### Step 1: NER Annotation

First, you must run the NER (Named Entity Recognition) annotation tool:

```
bash run.sh
```

This script will:
- Open necessary screens
- Launch the NER annotation interface for annotating facts and claims
- Save the annotations to the database

You must complete some annotations and ensure they are saved to the database before proceeding to Step 2.

### Step 2: Relation Annotation

Only after completing Step 1 and successfully saving annotations to the database, run:

```
bash run_relation.sh
```

This will start the relation annotation interface, allowing you to create relationships between the previously annotated entities.

## Important Notes

- The virtual environment **MUST** be named "Prodigy_Env" - this is not optional. The scripts specifically look for this environment name and will fail with any other name.
- Make sure both run.sh and run_relation.sh have execution permissions (`chmod +x run.sh run_relation.sh`).
- You must complete the NER annotation process and save data to the database before attempting to run the relation annotation tool.
- The two scripts must be run in the correct sequence (run.sh → run_relation.sh).

## Troubleshooting

If you encounter any issues:

1. Verify that the virtual environment is activated
2. Confirm that your virtual environment is exactly named "Prodigy_Env"
3. Check that all dependencies are installed correctly
4. Ensure run.sh and run_relation.sh have execution permissions
5. Make sure you've completed some NER annotations before trying to use the relation annotation tool

## Contact

For questions or support, please open do not contact us! <3