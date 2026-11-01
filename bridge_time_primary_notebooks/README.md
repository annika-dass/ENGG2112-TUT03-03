# Bridge deterioration — time-to-event primary workflow

## Important
This is a **new, separate modelling section**, not a replacement for your original project. Keep the original notebooks and results backed up. The new notebooks use the existing `data/final/` parquet files and save predictions to `results/`.

## Order
- `01_data_preparation_ORIGINAL` and `02_train_test_split_ORIGINAL`: **reference copies only**, do not rerun if the existing final parquet data are correct.
- `04_weibull_time_primary`: train Weibull, estimate conditional median remaining years, then calculate four-year risk.
- `05_cox_age_only_time_primary`: baseline Cox with median remaining years, then four-year risk.
- `06_cox_multivariable_time_primary`: multivariable Cox with median remaining years, then four-year risk.
- `07_rsf_time_primary`: original RSF with median remaining years, then four-year risk; initially 1,000 rows for time output.
- `08_model_improvements`: preserved original experiments.
- `09_tuning_time_primary`: preserved historical validation and tuning, plus tuned RSF median remaining years; initially 1,000 rows for time output.
- `10_deterioration_factors`: preserved descriptive factors.
- `11_time_prediction_evaluation`: compare median time prediction availability and ranking on matched rows.
- `12_four_year_risk_supplement`: preserved original risk evaluation, presented as supplementary.

## Technical qualifications
- `duration` means years since **first observed Good**, not years since bridge construction.
- The event is Good → Fair/Poor, **not structural collapse**.
- Median **remaining** time solves conditional survival = 0.5 at entry time; it is not necessarily unconditional median minus elapsed years.
- Cox and RSF return missing median where their learned survival curves do not cross 0.5 within support; Weibull extrapolates parametrically.
- C-index is ranking performance, **not average years prediction error**. Do not use it to claim that a specific deterioration year is accurate.
- Different model C-indices computed on different subsets cannot be directly compared. Notebook 11 creates a matched-row comparison.
- Four-year calibration is supplementary and cannot validate 10–20 year forecasts.
- **Notebooks have been syntax checked, not executed against full training/test parquet files.** Run locally, send outputs and errors, and verify before reporting results.
- If running notebooks from VS Code, set working directory to `notebooks/` under the existing project. Some preserved original notebooks rely on relative `../data/` paths.
- The original 05 Cox baseline code has a manually defined tail hazard extension for four-year risk; primary time predictions do **not** use that extrapolation.
- The original 09 tuning notebook may be memory-intensive; do not run on 8 GB RAM without reviewing its training configuration and closing other processes.

## Environment
Expected: pandas, numpy, matplotlib, pyarrow, lifelines, scikit-learn, scikit-survival, jupyter.

## Note on model selection
Do not choose a winning model based only on the C-index of the *subset with an estimable median*, since that subset can be unrepresentative. Report coverage and matched-subset performance. If very few bridges have finite medians, median time may not be a useful primary operational output; this is an empirical finding, not a coding failure.
