# Changelog

## [Unreleased]

## [1.0.0] - 2026-10-13

### Added

- Implemented protein and peptide quantification with two selectable protein grouping workflows: OpenMS ProteinInferencer and ProteinProphet.
- Added optional consensusXML merging, protein FDR filtering for the OpenMS workflow, and protein group preparation for the ProteinProphet workflow.
- Added FragPipe 24.0 execution for iProphet and ProteinProphet, with matching OpenMS and Python processing steps.
- Added shared schema, resource allocation, container profiles, and environment-driven NFTest integration cases for LFQ and TMT inputs with both grouping algorithms.
- Added pipeline documentation and a schematic showing the two separate grouping workflows and their inputs and outputs.
