# Integration tests

From the repository root, copy `.env-template` to `.env` and set `TEST_DATA_DIR` to the root containing the `ecoli_lfq`, `ecoli_tmt`, and `database` fixture directories. The Slurm launcher sources `.env`, which is ignored by Git. The template also pins the Nextflow version and config parser used by the completed pipelines.

The four NFTest cases exercise ProteinInferencer and ProteinProphet with LFQ and TMT inputs:

| Case | ConsensusXML input | Protein grouping input |
| --- | --- | --- |
| `test-integration-openms-lfq` | Final LFQ FileMerger consensusXML | OpenMS ProteinInference |
| `test-integration-proteinprophet-lfq` | Final LFQ FileMerger consensusXML | Unfiltered LFQ idXML files and target-decoy FASTA |
| `test-integration-openms-tmt` | Final TMT IDConflictResolver consensusXML for one E. coli plex | OpenMS ProteinInference |
| `test-integration-proteinprophet-tmt` | The same TMT consensusXML | Matching unfiltered PEP-scored `idswitch_pep.idXML` and target-decoy FASTA |

The TMT cases set `merge_consensus=false` because each takes one plex. The ProteinProphet inputs must retain decoy hits and use PEP as the active score. The ProteinProphet cases also exercise the lxml pepXML termini repair between IDFileConverter and iProphet. `test/csv_environment_expander.groovy` expands `$TEST_DATA_DIR` in the input CSVs before Nextflow reads them.

Run `test/run-nftest.sh <case-name>` inside a Slurm job from the repository root. The launcher uses `/scratch/$SLURM_JOB_ID` for work and sets `NFT_OUTPUT`. Confirm that each fixture path exists under `TEST_DATA_DIR` before running. Integration requires the configured OpenMS, pyOpenMS, and FragPipe containers and initialized shared config submodules.

The focused pepXML repair test can be run locally with `lxml` installed: `python3 -m unittest discover -s test -p test_fix_pepxml_termini.py`. The configured FragPipe 24.0 image includes `lxml`.
