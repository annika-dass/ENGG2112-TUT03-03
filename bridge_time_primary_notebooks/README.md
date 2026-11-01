# Bridge Deterioration Prediction Using Survival Analysis

## Project Overview

This ENGG2112 project investigates the time until bridges deteriorate from Good condition to Fair or Poor using survival analysis.

The project uses annual United States National Bridge Inventory (NBI) data from 1992 to 2025 to examine bridge deterioration patterns and compare different survival prediction models.

The objective is to estimate bridge deterioration times and investigate how bridge age, traffic volume, structural characteristics and condition ratings influence deterioration.

## Models

The project implements and compares the following survival analysis models:

1. **Age-only Cox Proportional Hazards Model** - A baseline model using bridge age.
2. **Multivariable Cox Proportional Hazards Model** - Uses multiple bridge characteristics to estimate deterioration risk.
3. **Weibull Accelerated Failure Time Model** - Estimates deterioration times using a parametric survival model.
4. **Random Survival Forest** - A machine learning survival model that captures nonlinear relationships.
5. **Improved Weibull and Random Survival Forest Models** - Additional models incorporating structural condition information and other improvements.

Model performance is evaluated primarily using the concordance index (C-index).

## Repository Structure

```text
ENGG2112-TUT03-03/
│
├── bridge_time_primary_notebooks/
│   └── notebooks/
│       ├── 01_data_preparation.ipynb
│       ├── 02_train_test_split.ipynb
│       ├── 03_weibull_time.ipynb
│       ├── 04_cox_age_only.ipynb
│       ├── 05_cox_multivariable_time.ipynb
│       ├── 06_rsf_time.ipynb
│       ├── 07_model_improvements.ipynb
│       ├── 08_deterioration_factors.ipynb
│       ├── 09_time_prediction_evaluation.ipynb
│       └── 10_rsf_weibull_improvements.ipynb
│
├── data/
│   ├── processed/
│   │   └── nbi_1992_clean.parquet ... nbi_2025_clean.parquet
│   └── final/
│       ├── bridge_survival_dataset.parquet
│       ├── bridge_survival_train.parquet
│       ├── bridge_survival_test.parquet
│       ├── bridge_survival_test_aligned.parquet
│       └── bridge_historical_validation.parquet
│
├── src/
├── results/
├── requirements.txt
└── README.md
```

## Installation

The project was developed using **Python 3.13.3**.

### 1. Clone the repository

```bash
git clone https://github.com/annika-dass/ENGG2112-TUT03-03.git
cd ENGG2112-TUT03-03
```

### 2. Create a virtual environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

The project uses Python libraries including:

- pandas and NumPy for data processing
- PyArrow for reading and writing Parquet files
- lifelines for Cox and Weibull survival models
- scikit-survival for Random Survival Forest modelling
- scikit-learn and SciPy for numerical and machine learning operations
- Matplotlib and Seaborn for visualisation
- Jupyter Notebook for executing the analysis

### 4. Launch Jupyter Notebook

From the repository root directory, run:

```bash
python -m notebook
```

Navigate to:

`bridge_time_primary_notebooks/notebooks/`

Open the required notebooks and select the Python environment containing the installed dependencies.

## Notebook Execution Order

The recommended order for the core analysis is:

| Order | Notebook | Purpose |
|---|---|---|
| 1 | `01_data_preparation.ipynb` | Prepare annual NBI data and construct the survival dataset |
| 2 | `02_train_test_split.ipynb` | Generate training, testing and aligned testing datasets |
| 3 | `04_cox_age_only.ipynb` | Train and evaluate the age-only Cox baseline |
| 4 | `05_cox_multivariable_time.ipynb` | Train and evaluate the multivariable Cox model |
| 5 | `03_weibull_time.ipynb` | Train and evaluate the Weibull AFT model |
| 6 | `06_rsf_time.ipynb` | Train and evaluate the Random Survival Forest |
| 7 | `09_time_prediction_evaluation.ipynb` | Compare model predictions and evaluation results |

Additional analysis notebooks are:

| Notebook | Purpose |
|---|---|
| `07_model_improvements.ipynb` | Explore improvements to the survival models |
| `08_deterioration_factors.ipynb` | Investigate factors associated with bridge deterioration |
| `10_rsf_weibull_improvements.ipynb` | Evaluate improved RSF and Weibull models, including historical validation |

The core order is intended to ensure that model predictions are generated before Notebook 09 attempts to load them. A complete fresh-environment execution of every notebook has not yet been verified.

## Data

### Data source

The project uses annual National Bridge Inventory data from 1992 to 2025.

Bridge condition is assessed using the available structural component ratings. The analysis focuses on bridges initially classified as Good and observes the time until their condition deteriorates to Fair or Poor.

Bridges that do not experience the defined deterioration event during their observation period are treated as censored observations.

### Processed datasets

The `data/processed/` directory contains cleaned annual NBI snapshots:

`nbi_1992_clean.parquet` through `nbi_2025_clean.parquet`

These files are included so that users can reproduce the survival analysis without downloading and cleaning the original NBI archives.

### Final survival datasets

The `data/final/` directory contains:

| Dataset | Description |
|---|---|
| `bridge_survival_dataset.parquet` | Original survival dataset containing bridge histories and deterioration outcomes |
| `bridge_survival_train.parquet` | Training dataset with the chronological training cutoff |
| `bridge_survival_test.parquet` | Testing cohort using predictor values from the 2021 testing baseline |
| `bridge_survival_test_aligned.parquet` | Same testing cohort with predictor values aligned to each bridge's original survival baseline |
| `bridge_historical_validation.parquet` | Dataset supporting historical validation |

### Aligned testing dataset

Notebook 02 generates the aligned testing dataset required by several modelling notebooks.

The aligned dataset contains **171,766 bridges and 15 columns**.

It preserves the testing cohort and survival outcomes while using the original survival-baseline values for five predictors:

- Bridge age
- Average daily traffic
- Structure kind
- Structure type
- Structure length

This distinction is important because the original testing dataset uses predictor values from 2021, whereas the aligned dataset uses the original survival-baseline predictors.

The aligned dataset can be regenerated by executing the final dataset-generation cell in Notebook 02.

## Reproducing the Analysis

### Option A: Use the supplied processed and final datasets

This is the recommended option for reviewing the modelling work.

1. Clone the repository and install the Python dependencies.
2. Launch Jupyter Notebook from the repository root.
3. Open the notebooks in `bridge_time_primary_notebooks/notebooks/`.
4. Use the supplied datasets in `data/processed/` and `data/final/`.
5. Execute the model notebooks in the recommended core order.
6. Run Notebook 09 after the required model prediction CSV files have been generated.
7. Run the additional analysis notebooks as needed.

The supplied datasets allow the modelling analysis to be performed without repeating the original NBI download and cleaning process.

### Option B: Regenerate the datasets

To reproduce the earlier data preparation stages:

1. Obtain the original annual NBI source files.
2. Make the files available in the raw-data location expected by Notebook 01.
3. Run Notebook 01 to prepare the survival dataset.
4. Run Notebook 02 to generate the training, testing and aligned testing datasets.
5. Execute the modelling notebooks in the recommended order.

The original raw NBI archives are not included in this repository because of their size.

Regenerating the datasets may require substantial processing time and storage.

## Model Evaluation

The primary evaluation metric is the **concordance index (C-index)**.

The C-index measures how effectively a survival model ranks observations according to their predicted deterioration risk or survival time.

The project compares the performance of the age-only Cox baseline against more complex survival models.

Additional analysis examines the influence of bridge characteristics, traffic volume and structural condition ratings on deterioration predictions.

## Reproducibility Notes

- Run Jupyter from the repository root so that the notebooks can locate the project directories.
- The cleaned annual NBI datasets and final survival datasets are included.
- Notebook 02 generates the aligned testing dataset used by the modelling notebooks.
- Notebook 09 requires prediction CSV files produced by earlier modelling notebooks.
- Model training times depend on available hardware and may be substantial.
- The raw NBI archives are not included.
- The complete workflow has not yet been independently verified through a fresh-environment execution of all notebooks.

