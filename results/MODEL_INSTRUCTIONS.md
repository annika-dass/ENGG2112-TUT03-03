# ENGG2112 — Shared Survival Modelling Instructions

**Read this document and the two supplied Parquet files before writing model code.** These instructions are for group members and their AI coding assistants. The shared data preparation is complete; do **not** repeat it or make a random train/test split.

## 1. Project goal

Predict deterioration of US bridges from **Good** to **Fair or Poor**, using historical Federal Highway Administration National Bridge Inventory (NBI) observations. Compare four survival-analysis models on the **same** test cohort:

| Model | Predictors | Required output file | Risk column |
|---|---|---|---|
| Age-only Cox proportional hazards (baseline) | `bridge_age` only | `cox_baseline_predictions.csv` | `cox_baseline_risk` |
| Multivariable Cox proportional hazards | Five shared predictors below | `cox_multivariable_predictions.csv` | `cox_multivariable_risk` |
| Random Survival Forest | Five shared predictors below | `rsf_predictions.csv` | `rsf_risk` |
| Weibull accelerated failure time (AFT) | Five shared predictors below | `weibull_aft_predictions.csv` | `weibull_aft_risk` |

**Only implement the model assigned to you.** The group coordinator will combine and evaluate the outputs centrally.

## 2. Files supplied

- `bridge_survival_train.parquet` — **498,875** bridge records. Bridges first observed Good during 1992–2020; observed follow-up is censored at the end of 2020.
- `bridge_survival_test_aligned.parquet` — **171,766** bridges observed Good in 2021, followed through 2025 where possible. This file uses the **original Good-baseline predictor values**, not updated 2021 values.
- `01_data_preparation.ipynb` and `02_train_test_split.ipynb` (if provided) — reference only; you should not need to execute them.

The data are already cleaned and survival outcomes are constructed. Use the supplied datasets unchanged except for model-specific preprocessing. Some bridge IDs occur in both datasets: this is a **temporal forecast of previously observed bridges**, not an independent-bridge holdout.

## 3. Column definitions

| Column | Meaning |
|---|---|
| `bridge_id` | Unique bridge identifier; preserve exactly as a string |
| `duration` | Observed time in years since the bridge's first Good observation |
| `event` | 1 = observed deterioration to Fair/Poor; 0 = right-censored |
| `bridge_age` | Bridge age at first observed Good condition |
| `ADT_029` | Average daily traffic at original Good baseline |
| `STRUCTURE_LEN_MT_049` | Structure length in metres at original Good baseline |
| `STRUCTURE_KIND_043A` | Structure-kind category |
| `STRUCTURE_TYPE_043B` | Structure-type category |
| `entry_duration` | **Test only:** years already survived from first Good observation to 2021 |
| `test_duration` | **Test only:** observed follow-up in years from 2021 (up to four elapsed years) |

Five shared predictors for non-baseline models:

```python
PREDICTOR_COLUMNS = [
    "bridge_age",
    "ADT_029",
    "STRUCTURE_LEN_MT_049",
    "STRUCTURE_KIND_043A",
    "STRUCTURE_TYPE_043B",
]
```

**Never use** `event`, `duration`, `test_duration`, `end_year`, `stop_reason`, `last_year`, or any future-observation information as model predictors. `entry_duration` is used to **condition test predictions**, not as a fitted baseline predictor. Do not use bridge IDs as predictive features.

## 4. Model fitting

1. Load the supplied Parquet files using pandas; check their row counts and required columns.
2. Fit on the **training file only**, using `duration` as survival time and `event` as event indicator. All training durations must be positive.
3. Handle missing predictors using parameters estimated from **training only** (for example, median numeric imputation and most-frequent categorical imputation). Apply the same fitted transformations to test data.
4. Encode categorical structure variables appropriately, fitting the encoder on training data only. Handle unseen test categories safely. The baseline Cox model must use **only `bridge_age`**.
5. Check model convergence and whether fitted survival curves are finite and non-increasing. If an algorithm cannot handle this dataset at full size, document and justify any computational compromise; **do not silently change the cohort or outcome**.
6. Do not use test outcomes to choose predictors, tune hyperparameters, or fit preprocessing. The central evaluator alone will use test outcomes for final scoring.

The survival clock is **time since first observed Good**, not calendar year and not age since construction.

## 5. Shared prediction task — essential

The test question is: **For a bridge known to be Good in 2021, what is the probability it deteriorates by 2025?**

2021 to 2025 is **four elapsed years**. Each model must predict the survival function \(S(t\mid X)\), then compute for every test bridge:

\[
\text{risk}_{2021\to2025} = 1 - \frac{S(a+4\mid X)}{S(a\mid X)},
\quad a=\texttt{entry_duration}.
\]

Here, \(X\) is the bridge's **original Good-baseline** predictor vector from `bridge_survival_test_aligned.parquet`. A bridge with `entry_duration = 18` needs survival predictions at **18 and 22 years** since its original Good observation, **not** at years 0 and 4. A bridge with entry 0 uses survival at years 0 and 4.

Implementation notes:

- Evaluate both survival probabilities **for the same bridge and its predictors**.
- Ensure survival predictions cover the required time points; be especially careful with Random Survival Forest step functions and prediction times beyond the last fitted event time. Do not silently extrapolate unsupported predictions.
- Handle extremely small \(S(a)\) carefully, and investigate rather than silently accepting invalid or non-finite results.
- The resulting risk must be finite and in **[0, 1]**. Higher risk means earlier expected deterioration.
- The model must **not** use `test_duration` or test `event` when producing risk predictions.

### Example

If a model estimates \(S(18)=0.80\) and \(S(22)=0.72\), the conditional four-year risk is \(1-0.72/0.80=0.10\), or 10%.

## 6. Required deliverables

Save one CSV in the project's `results/` directory (or return it to the coordinator for placement there). It must contain **exactly 171,766 rows**, one for each test bridge, and exactly these two columns:

```text
bridge_id,<your_model_risk_column>
```

Use the filename and risk-column name from Section 1 **exactly**. Preserve `bridge_id` strings, including leading zeros and letters. Verify:

- No missing or duplicated bridge IDs.
- All test IDs are represented exactly once; no extra IDs.
- No missing, infinite, negative, or greater-than-one risks.
- The predictions correspond to **conditional four-year risks**, not raw Cox hazard ratios, median survival times, or unconditional four-year survival probabilities.

Also provide your reproducible model notebook and a brief description of preprocessing, fitted parameters/hyperparameters, software packages, and any convergence or computational issues.

## 7. Evaluation (performed centrally)

The coordinator will match predictions by `bridge_id` and calculate a **censoring-aware Harrell concordance index** using `test_duration`, test `event`, and **negative predicted risk** as the predicted survival ordering (higher risk means shorter survival). The shared project aims for **C-index ≥ 0.70** and **an improvement of at least 0.05 over the age-only Cox baseline** for the advanced models. These are targets, not guaranteed results.

Important interpretation:

- The C-index evaluates **ranking/discrimination** over the observed test follow-up, not accuracy of the exact deterioration year or calibration of four-year probabilities.
- The 2021–2025 window has at most four elapsed years; it **cannot directly validate 10- or 20-year forecasts**.
- Harrell's C-index uses comparable event/censoring pairs; informative censoring may bias estimates.
- The 2021 survivor cohort is selected conditional on still being Good, and some bridge identities appear in training. The evaluation is **not independent-bridge generalisation**.
- Predictors are fixed at the original Good baseline, so the models do **not** incorporate updated 2021 traffic, age, or structural measurements.
- The chosen conditional-risk score and ordinary C-index are a practical common comparison; they do not establish perfect statistical calibration. Do not overstate conclusions.

## 8. Instructions to your AI coding assistant

> Help me build **only my assigned model** for the ENGG2112 bridge deterioration project using the two provided Parquet datasets and this instruction document. Explain code in simple English. Work **one notebook cell at a time** and wait for my output before continuing. Do not redo data cleaning, change the train/test split, or invent results. Fit all preprocessing using training data only. Produce a correct conditional four-year deterioration risk for every test bridge, save the CSV with the exact required filename and column name, and verify its IDs and risk values. Flag any methodological or computational problem rather than silently changing the task.

## 9. Quick checklist before submission

- [ ] Trained only on the provided training data.
- [ ] Used the correct predictor set for my assigned model.
- [ ] Preprocessing fitted on training data only.
- [ ] Used `entry_duration` and conditional survival to calculate four-year risk.
- [ ] Did not use test outcomes to fit or tune the model.
- [ ] Exported 171,766 unique bridge IDs with valid probabilities.
- [ ] Named CSV and risk column exactly as required.
- [ ] Submitted the notebook and documented limitations.
