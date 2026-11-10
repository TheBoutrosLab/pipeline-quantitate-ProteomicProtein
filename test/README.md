# Integration tests

From the repository root, copy `.env-template` to `.env` and set `TEST_DATA_DIR` to the root containing the LFQ, TMT, and database fixtures. Each case passes one consensusXML path directly. Both TMT cases use the cohort-level `ecoli_tmt_IDConflictResolver.consensusXML` under `TEST_DATA_DIR`; the ProteinProphet TMT case uses its local unfiltered idXML path CSV. The Slurm launcher sources `.env`, which is ignored by Git. The template also pins the Nextflow version and config parser used by the completed pipelines.

The four NFTest cases exercise ProteinInferencer and ProteinProphet with LFQ and TMT inputs:

| Case | ConsensusXML input | Protein grouping input |
| --- | --- | --- |
| `test-integration-openms-lfq` | Final LFQ FileMerger consensusXML | OpenMS ProteinInference |
| `test-integration-proteinprophet-lfq` | Final LFQ FileMerger consensusXML | Unfiltered LFQ idXML files and target-decoy FASTA |
| `test-integration-openms-tmt` | Final multi-plex cohort TMT consensusXML under `TEST_DATA_DIR` | OpenMS ProteinInference |
| `test-integration-proteinprophet-tmt` | The same TMT cohort consensusXML | Matching unfiltered PEP-scored idXML list and target-decoy FASTA |

The final protein CSV has sample-level quantities with explicit plex and reporter channel headers for TMT, or sample headers for LFQ. The ProteinProphet inputs must retain decoy hits and use PEP as the active score. The ProteinProphet cases also exercise the lxml pepXML termini repair between IDFileConverter and iProphet. `test/csv_environment_expander.groovy` expands environment variables in the remaining unfiltered idXML input CSVs before Nextflow reads them.

Both ProteinProphet cases set `save_intermediate_files=true` to retain intermediate artifacts. The raw `<project_name>_ProteinProphet.protXML` and filtered `<project_name>_ProteinProphet_filtered.idXML` are also published in the final output directory independently of this setting. The filtered idXML is the file passed to ProteinQuantifier.

Run `test/run-nftest.sh <case-name>` inside a Slurm job from the repository root. The launcher uses `/scratch/$SLURM_JOB_ID` for work and sets `NFT_OUTPUT`. Confirm that each fixture path exists under `TEST_DATA_DIR` before running. Integration requires the configured OpenMS, pyOpenMS, and FragPipe containers and initialized shared config submodules.
