# Task 02 findings

## A different representation of political ads

The Task 2 source contains **246,745 rows and 41 columns**. Although its row count matches Task 1, its schema and values are different. It includes numeric `estimated_spend`, `estimated_impressions`, and `estimated_audience_size`, nested regional and demographic distributions, and anonymized page IDs. It omits the earlier page names and delivery dates. The core analysis identifies 31 numeric columns, nine categorical columns, and one date column. These changes make copying the earlier conclusions without rerunning the analysis inappropriate.

## What grouping reveals

There are **4,475 distinct page groups** and **246,745 distinct page/ad groups**. Every page/ad pair occurs exactly once. Consequently, the mean, minimum, maximum, and median of a present numeric value are identical within each page/ad group, while sample standard deviation is undefined. Returning zero standard deviation would falsely suggest that sample variability had been estimated. The test fixture includes a repeated page/ad pair, so the multi-row path is tested even though it does not occur in the supplied file.

Page grouping provides a more informative view of concentration. The file contains 18 currencies, including 246,599 USD records. Estimated USD spending totals **$261,764,951**. The largest page-level USD totals are shown below. Page IDs are shortened for readability; full IDs are preserved in `results/findings.json`. Bylines describe the most frequent sponsor text within each page group, not verified page names or comprehensive organization totals.

| Page ID prefix | Most frequent byline | Records | Estimated USD spending |
|---|---|---:|---:|
| `4d66f5853f03` | HARRIS FOR PRESIDENT | 55,503 | $82,795,647 |
| `4ade40418626` | BIDEN VICTORY FUND | 14,822 | $26,367,978 |
| `e3342051b603` | DONALD J. TRUMP FOR PRESIDENT 2024, INC. | 23,988 | $19,609,362 |
| `ec8ac6dc1cdd` | HARRIS VICTORY FUND | 9,851 | $10,599,999 |
| `e3ee066f4a12` | HARRIS VICTORY FUND | 6,581 | $7,634,469 |

The three largest pages account for approximately **49.2%** of estimated USD spending in this dataset. This indicates substantial page-level concentration. It does not establish total campaign spending, and repeated sponsor names should not be interpreted as independent organizations. One page contains multiple currencies; monetary interpretation must therefore filter currency even after grouping by page.

## Timing and content

October 2024 contains **84,397 ad creation records (34.20%)**, the largest month in the file. Some creation dates predate 2024, reaching back to July 2021. These are creation counts, not monthly expenditures or delivery counts. The small November slice is incomplete, so its low count cannot establish a general decline in advertising.

Exact mention strings include Donald Trump in 78,324 records, Kamala Harris in 53,239, and Joe Biden in 24,247. President Trump and President Biden appear separately and have not been merged with other aliases. Counts overlap when a record mentions more than one person. They do not measure endorsement, sentiment, electoral support, or ownership of the ad.

Facebook appears in 238,350 platform lists and Instagram in 223,434; many records include both. Among classification flags, call-to-action is present in 141,328 records and advocacy in 135,372. Classification values are reported as supplied labels rather than independently verified descriptions of the underlying creative.

## Structured values and missing information

Only `bylines` contains missing scalar cells under the documented conventions: **1,009 records (0.409%)**. This superficially high completeness conceals missing substantive detail. Both regional and demographic fields contain **30,989 empty dictionaries**, and mentions contain **73,205 empty lists**. An empty structure is a valid stored value, but does not supply a geographic distribution, demographic breakdown, or detected candidate mention. Empty mentions should not be used to prove that the ad's original text mentioned no candidate.

All four structured fields parsed without a syntax or checked-shape error using `ast.literal_eval`. Parsing success does not establish the accuracy or completeness of their contents. For regional USD estimates, Pennsylvania has the largest recorded total ($31,125,548), followed by Michigan ($26,464,745) and California ($19,593,833). These totals describe available regional allocations and exclude information absent from empty dictionaries. They are not causal evidence of targeting strategy or complete regional campaign budgets.

## Interpretation limits

The three estimated metrics are supplied point estimates. This file does not include the original uncertainty intervals, so these numbers must not be presented as exact observed spend, reach, or impressions. Audience estimates may overlap across ads and cannot be summed into unique people. Core descriptive spending statistics across currencies are included for completeness but have no single monetary unit; USD-only findings provide the interpretable spending comparison.

The agreement check evaluates every statistic for every group, not a sample. Shared cleaning rules and singleton identities remain common assumptions, so agreement alone cannot validate the underlying estimates, classification quality, or sampling coverage. The published results include the overall summaries, all page-level estimated-metric summaries, selected complete group examples, and the comparison record; the scripts regenerate the full grouped outputs locally.
