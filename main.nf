nextflow.enable.dsl = 2

include { infer_proteins } from "${projectDir}/modules/infer_proteins"
include { filter_proteins } from "${projectDir}/modules/filter_proteins"
include { resolve_conflict } from "${projectDir}/modules/resolve_conflict"
include { quantify_proteins } from "${projectDir}/modules/quantify_proteins"
include { reheader_ProteinQuantCSV } from "${projectDir}/modules/reheader_ProteinQuantCSV"
include { reheader_PeptideQuantCSV } from "${projectDir}/modules/reheader_PeptideQuantCSV"
include { set_databasePath } from "${projectDir}/modules/set_databasePath"
include { extract_enzyme_rule } from "${projectDir}/modules/extract_enzyme_rule"
include { run_iProphet } from "${projectDir}/modules/run_iProphet"
include { run_ProteinProphet } from "${projectDir}/modules/run_ProteinProphet"
include { convert_idXML2pepXML } from "${projectDir}/modules/convert_idXML2pepXML"
include { fix_pepxml_termini } from "${projectDir}/modules/fix_pepxml_termini"
include { convert_protXML2idXML } from "${projectDir}/modules/convert_protXML2idXML"
include { filter_protein_groups } from "${projectDir}/modules/filter_protein_groups"

include { print_prelogue } from "${projectDir}/modules/common"

print_prelogue()

workflow {
    consensusXML = file(params.input_consensusXML)

    if (params.protein_grouping_algorithm == 'ProteinProphet') {
        ich_unfiltered_idXML = Channel.fromPath(params.unfiltered_idXML)
            .splitCsv(header:true)
            .map { file(it.path) }

        // We assume the same decoy database is used across samples in a project. The path however
        // can be different because of soft links. Have to set them all to the same value otherwise
        // ProteinProphet will complain.
        set_databasePath(ich_unfiltered_idXML, file(params.decoy_database))
        extract_enzyme_rule(set_databasePath.out[0])
        convert_idXML2pepXML(extract_enzyme_rule.out[0])
        fix_pepxml_termini(convert_idXML2pepXML.out[0])
        run_iProphet(fix_pepxml_termini.out[0].collect(), file(params.decoy_database))
        run_ProteinProphet(run_iProphet.out[0], file(params.decoy_database))
        convert_protXML2idXML(run_ProteinProphet.out[0])
        filter_protein_groups(convert_protXML2idXML.out[0])
        protein_groups = filter_protein_groups.out[0]
        final_consensusXML = consensusXML
    } else {
        // OpenMS::ProteinInferencer
        infer_proteins(consensusXML)

        if (params.protein_inference_protein_fdr == true && params.filter_protein_fdr == true) {
            filter_proteins(infer_proteins.out[0])
            consensusXML_inferred = filter_proteins.out[0]
        } else {
            consensusXML_inferred = infer_proteins.out[0]
        }
        resolve_conflict(consensusXML_inferred)
        final_consensusXML = resolve_conflict.out[0]
        protein_groups = file("${projectDir}/input/NO_FILE")
    }
    quantify_proteins(final_consensusXML, protein_groups)
    reheader_ProteinQuantCSV(quantify_proteins.out[0].map { protein, peptide, consensus -> tuple(protein, consensus) })
    reheader_PeptideQuantCSV(quantify_proteins.out[0].map { protein, peptide, consensus -> tuple(peptide, consensus) })
}
