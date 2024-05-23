# Scripts in order of execution:
- `extract_KR_numbers.py`: Searches for parallel editions in the Kanripo. Needs the [Kanripo catalogue](https://github.com/kanripo/KR-Catalog)
to be present in a directory `KR-Catalog-master`.
- `download_kr.sh`: Downloads the parallel editions into directory `corpus`.
- `unzip_corpus.sh`: Unzips the downloaded editions.
- `extract_text.py`: Extracts and cleans the raw texts from the corpus. 
- `hirschberg.py`: Computes the alignments.
- `find_candidates.py`: Search the alignments for candidates for differentiation and not differentiated variants in pairs of editions.
- `compute_embeddings.py`: Computes contextual embeddings for each line in `parallel_passages.csv`.
- `regression_by_document.py`: First experiment, fits logistic regressions for each individual pair of substitution profile and document.
- `regression_cross_document.py`: Second experiment, fits logistic regressions on single documents and tests on different document.
- `regression_li_li.py`: Fit regression on multiple documents differentiating 歷 and 曆.
- `variants.R`: Collect descriptive statistics and do significance testing.

# Data files:
- `dual_kr_ids.txt`: List of Kanripo numbers with dual editions.
- `texts.csv`: Extracted texts.
- `alignments.csv`: Results of alignment.
- `substitution_profiles.csv`: Substitution profiles.
- `parallel_passages.csv`: Samples for substitution profiles.
- `embeddings.npy` (not included due to large size): Contextual embeddings.
- `regression_predictions_*.csv`: Predictions on the test sets of the various logistic models.
- `kr_number_to_title_dynasty_author.csv`: Metadata extracted from the Kanripo catalogue.
