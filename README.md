# Task 02: Descriptive Statistics with Python, Pandas, and Polars

This project implements Milestone A of Research Tasks 2 and 3. It computes descriptive statistics independently with standard-library Python, Pandas, and Polars, then checks agreement for the complete dataset, every page, and every page/ad combination.

## Dataset and scope

Download the [Task 2 Facebook ads ZIP](https://drive.google.com/file/d/1UPo11lH2Mlk2cnLtjv8P9XqlKitms-gp/view?usp=sharing), extract it, and place `2024_fb_ads_president_scored_anon.csv` in a local `data/` folder. This is the Task 2 source, not the Task 1 CSV. The analyzed file has 246,745 rows and 41 columns. Its SHA-256 is recorded in the generated overall summaries and comparison report.

The raw CSV, source ZIP, and full record-level output archives are deliberately excluded from GitHub. Full group outputs are regenerated locally by the commands below. Compact overall summaries, page-level numeric results, examples, and validation evidence are included in `results/`.

## Setup and run

Use Python 3.11 or later. Python 3.12 was used for validation. From the repository root:

```bash
python -m pip install -r requirements.txt
python -m unittest -v test_stats
python pure_python_stats.py data/2024_fb_ads_president_scored_anon.csv
python pandas_stats.py data/2024_fb_ads_president_scored_anon.csv
python polars_stats.py data/2024_fb_ads_president_scored_anon.csv
python compare_results.py
python analyze_findings.py data/2024_fb_ads_president_scored_anon.csv
python export_review_results.py
```

The standard-library script imports no third-party packages. Pandas and Polars are pinned in `requirements.txt`. Each engine accepts `--out-dir` to override `outputs/<engine>/`; use the defaults for the comparison and export commands. Full grouped outputs are large, so allow several GB of free disk space and several GB of RAM. Run the three engines sequentially on a personal computer.

## What is calculated

At all three levels (whole dataset, `page_id`, and `page_id` plus `ad_id`):

- Numeric columns: nonmissing count, missing count/percentage, mean, minimum, maximum, sample standard deviation, median.
- Nonnumeric columns: nonmissing count, missing count/percentage, unique count, mode and frequency, and top five values.
- Every group includes its key and row count. Global column names, column count, and inferred types are recorded in the manifest and overall summary.

Python groups records with dictionaries. Pandas uses `groupby`, native grouped counts, `describe`, `value_counts`, `nunique`, and numeric reducers. Polars uses `group_by`, native grouped counts/index aggregation, expression-based numeric summaries, `value_counts`, and `n_unique`.

Shared `common.py` defines input conventions, output formatting and exact singleton identities. Multi-row statistical calculations are implemented separately in each engine. This makes comparisons independent for aggregation while keeping the data interpretation consistent. It does not claim to independently validate the shared cleaning rules.

## Cleaning and statistical decisions

1. Trim strings. Empty strings and case-insensitive NA, N/A, null, none and nan are missing. Numeric cleaning removes commas, a leading dollar sign, and accounting parentheses. Non-finite numbers are not treated as valid numeric values.
2. A column is numeric only when every nonmissing value converts to a finite number. Mixed text/numeric columns remain categorical. IDs and scored-message hashes remain categorical. ISO dates are identified separately.
3. Infer types once from the full input and retain them inside groups. An all-null subgroup of a numeric column therefore remains numeric.
4. Standard deviation uses `ddof=1`. Zero or one numeric observation gives null standard deviation. Counts and category matches are exact; float comparisons use relative and absolute tolerance `1e-9`.
5. Ties in modes/top five are resolved lexicographically. Missing grouping keys are retained rather than dropped.
6. All page/ad pairs in the supplied file are singletons. After each engine's grouping step identifies them, the output formatter applies exact singleton identities: mean/min/max/median equal the value; standard deviation is null. The tests also include repeated pairs, ensuring the general aggregation path works.
7. Lists and dictionaries receive exact-string categorical summaries in the core scripts. `analyze_findings.py` safely parses them with `ast.literal_eval`, validates their shapes, and counts each distinct mention/platform once per record. It does not execute cell contents. Empty lists/dictionaries are valid structures and are distinguished from missing scalar cells.
8. Generic spending statistics across all rows are mechanical numeric summaries across mixed currencies, not dollar amounts. Substantive spending findings use USD-only records. Page-level output can also mix currencies; consult the findings report's mixed-currency check before interpreting it monetarily.

## Output format

Each engine writes `overall.json`, `manifest.json`, `runtime.json`, `by_page.jsonl.gz`, and `by_page_ad.jsonl.gz`. Each compressed JSONL line contains a group key, row count, and statistics arrays. The manifest lists column order and the field names for numeric/categorical arrays. This compact representation contains every required statistic for every group.

`results/by_page_examples.json` and `results/by_page_ad_examples.json` show a few groups expanded into readable field names. `results/page_numeric_summary.csv` contains the three estimated metrics for all pages. `results/comparison.json` records validation across the complete local outputs, not just the published examples. Full per-ad outputs are omitted because of their size and because singleton summaries reproduce much of the underlying dataset.

## Validation result

All three engines agree at the whole-dataset level, for all 4,475 page groups, and for all 246,745 page/ad groups. The streaming comparison completed 166,470,018 pairwise leaf checks. Both automated tests passed. The USD spending total and largest USD page total were also independently checked with Pandas. See `results/comparison.json`, `results/test_results.txt`, and `results/findings_validation.txt`.

## Findings and reflection

See [FINDINGS.md](FINDINGS.md) for substantive results, [REFLECTION.md](REFLECTION.md) for the comparison and AI-code evaluation, and [results](results/) for supporting evidence. The major structural finding is that page grouping reveals between-page differences while page/ad grouping adds no within-group distribution in this particular file.

## GitHub submission

Create a public repository named **Task_02_Descriptive_Stats**. Upload the project files and the entire `results/` folder, including `.gitignore`. Do not upload the dataset, downloaded ZIP, or `outputs/`. GitHub's browser uploader does not enforce `.gitignore`; exclude these manually. Submit the repository link through your agreed course submission channel.

## Assistance and reproducibility

Code and report drafts were prepared with AI assistance and executed on the assignment's actual Task 2 CSV. No personal hours, unperformed manual work, or experiences are claimed. Review the reasoning and rerun the commands before submitting. This repository covers Task 2 only; cross-platform generalization belongs to Task 3.
