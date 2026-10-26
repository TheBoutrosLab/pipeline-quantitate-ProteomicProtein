# Changelog

## [Unreleased] - 2026-10-25

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
[unreleased]: https://github.com/TheBoutrosLab/pipeline-quantitate-ProteomicProtein/compare/v1.1.0...HEAD
