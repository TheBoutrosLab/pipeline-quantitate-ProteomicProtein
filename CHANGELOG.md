# Changelog

## [Unreleased]

### Changed

- Upgrade OpenMS and pyOpenMS defaults to 3.6.0, use its `best_charge` flag and explicit fraction aggregation, and reject removed ProteinQuantifier settings (2026-11-11).
- Map assay-level protein abundance headers by fraction group and label so fractions and technical replicates keep their OpenMS 3.6 meaning (2026-11-11).
- Apply the same readable assay headers to peptide abundances and annotate detailed peptide file/channel headers when descriptions are present (2026-11-11).

## [1.2.0] - 2026-11-09

### Added

- Label sample-level ProteinQuantifier protein abundance columns from the quantified consensusXML without changing abundance values.
- Accept one cohort-level consensusXML path directly and remove the consensusXML CSV and merge setting.

### Fixed

- Configure the repository's Python linter to ignore complexity limits and document the protein reheader CLI entry point (2026-11-09).

## [1.1.2] - 2026-10-26

### Added

- Publish the filtered ProteinProphet grouping idXML used by ProteinQuantifier in the final output directory on every run, with a stable filename.
- Publish the unfiltered ProteinProphet protXML in the final output directory on every run.
- Document the final grouping artifact for both ProteinProphet and ProteinInferencer.

## [1.1.1] - 2026-10-25

### Fixed

- Pass ProteinQuantifier `-top:include_all` as a standalone flag when enabled.

## [1.1.0] - 2026-10-25

### Fixed

- Repair OpenMS pepXML enzymatic-terminus annotations before iProphet so ProteinProphet can use PEP-derived probabilities for Trypsin/P and other C-terminal enzyme rules.
- Extract the OpenMS enzyme rule in a dedicated process and use it to repair both N-terminal and C-terminal cleavage annotations instead of trusting OpenMS-exported pepXML `sense`.
- Fail before ProteinQuantifier when ProteinProphet supplies no positive-probability groups.
- Preserve separate parent and indistinguishable protein groups when filtering ProteinProphet or future Fido inference results.
- Warn when a retained protein group contains a zero-scored protein hit that remains in a quantifiable indistinguishable subgroup.

## [1.0.0] - 2026-10-13

### Added

- Implemented protein and peptide quantification with two selectable protein grouping workflows: OpenMS ProteinInferencer and ProteinProphet.
- Added optional consensusXML merging, protein FDR filtering for the OpenMS workflow, and protein group preparation for the ProteinProphet workflow.
- Added FragPipe 24.0 execution for iProphet and ProteinProphet, with matching OpenMS and Python processing steps.
- Added shared schema, resource allocation, container profiles, and environment-driven NFTest integration cases for LFQ and TMT inputs with both grouping algorithms.
- Added pipeline documentation and a schematic showing the two separate grouping workflows and their inputs and outputs.

[1.0.0]: https://github.com/TheBoutrosLab/pipeline-quantitate-ProteomicProtein/releases/tag/v1.0.0
[1.1.0]: https://github.com/TheBoutrosLab/pipeline-quantitate-ProteomicProtein/compare/v1.0.0...v1.1.0
[1.1.1]: https://github.com/TheBoutrosLab/pipeline-quantitate-ProteomicProtein/compare/v1.1.0...v1.1.1
[1.1.2]: https://github.com/TheBoutrosLab/pipeline-quantitate-ProteomicProtein/compare/v1.1.1...v1.1.2
[1.2.0]: https://github.com/TheBoutrosLab/pipeline-quantitate-ProteomicProtein/compare/v1.1.2...v1.2.0
[unreleased]: https://github.com/TheBoutrosLab/pipeline-quantitate-ProteomicProtein/compare/v1.2.0...HEAD
