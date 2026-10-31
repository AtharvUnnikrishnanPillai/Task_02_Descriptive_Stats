# Comparing pure Python, Pandas, and Polars

## Achieving agreement

The three implementations use separate multi-row statistical calculations. Pure Python explicitly sorts values for the median, counts categories with `Counter`, and computes sample variance using `math.fsum`. Pandas uses its Series reducers, `value_counts`, `nunique`, and native grouping. Polars uses expression-based numeric reducers, `value_counts`, `n_unique`, and `group_by` to construct groups. Their canonical outputs are compared across the complete dataset and both required grouping levels.

Consistent semantics matter more than matching method names. The implementations share explicit cleaning rules, global type inference, lexicographic tie-breaking, and sample standard deviation. All-null subgroups retain their globally inferred numeric types. Missing grouping keys are kept, whereas dropping them would silently lose records. Integer counts and category values must match exactly, while floating-point values allow `1e-9` relative/absolute tolerance.

There are no repeated page/ad pairs in the supplied file. Once grouping identifies a singleton, a shared formatter uses mathematical identities rather than invoking a costly reducer for every metric. This is transparent reuse, but it also limits the independence of singleton validation. The synthetic test therefore includes repeated page/ad pairs and checks known multi-row means, medians and standard deviations. It also covers null grouping keys, all-empty columns, zeros, mixed text/numeric values, currency formatting, and tied categories.

## Developer experience and performance

Pure Python requires the most explicit work: grouping dictionaries, counts, sorting, null filtering, and variance formulas. That visibility helps explain why a result is correct. Pandas provides familiar column operations and convenient summaries, while Polars makes typed expressions and aggregation aliases explicit. Both DataFrame versions still use per-group Python orchestration in this implementation, so they are not fully optimized vectorized pipelines.

The scripts record elapsed time for each execution, but the validation runs overlapped and competed for resources. Those timings are not a controlled performance benchmark and are not used to rank the libraries. A fair future benchmark would run each implementation sequentially several times, distinguish input/output from computation, control thread counts, and report memory as well as time. No claim about universal library speed follows from this project.

For a junior analyst, I would recommend a small standard-library exercise first, followed by Pandas for routine tabular work and then Polars to learn expression-oriented operations. That order exposes the statistical decisions before relying on abstractions. The best production choice depends on workload, memory limits, existing code, and maintainability.

## Complex values and interpretation

The nested regional and demographic dictionaries cannot be averaged as strings. The core summaries describe exact stored strings, while a separate script parses the structures safely and validates their expected shapes. Empty dictionaries and lists are counted explicitly rather than confused with missing scalar cells. Mention and platform counts deduplicate items within each record; totals can overlap across categories.

The schema inspection also identified numeric-looking identifiers that must remain categorical and monetary values across 18 currencies. One page uses multiple currencies, demonstrating that grouping alone does not make a spending mean meaningful. USD-specific interpretation is therefore separate from generic numeric summaries.

## Evaluation of AI-assisted starter code

This project was prepared with AI assistance. The evidence concerns this implementation session, not a controlled experiment comparing ChatGPT, Claude, or Copilot. AI-generated scaffolding was useful for organizing loaders, reducers, grouping, output schemas and tests, but it needed execution and inspection.

A concrete issue arose in the Polars loader: the first draft supplied `missing_utf8_is_empty_string`, which the installed Polars 2.1.0 rejected. Inspecting the installed API and removing the obsolete argument resolved the problem, and the three-engine test then passed. This illustrates why plausible-looking API calls are not sufficient evidence of working code.

Other design decisions required explicit review: choosing `ddof=1`, keeping null grouping keys, separating currencies, and not asserting a geographic or demographic distribution for empty dictionaries. Generic AI summaries can also mistake estimates for exact measurements or infer that candidate mentions represent endorsements. Those interpretations were excluded from the findings.

No independent developer-effort study or multi-model comparison was performed. The supported conclusion is that starter code can accelerate setup, but correctness requires a clear statistical contract, known-answer tests, actual execution, and domain-aware interpretation. The submitter should adapt this reflection to describe their own review and learning accurately.
