/** Label OpenMS 3.6 peptide abundances using the quantified consensusXML. */
process reheader_PeptideQuantCSV {
    container params.docker_image_pyopenms
    containerOptions params.project_script_mount_options

    publishDir params.final_output_dir,
        mode: 'copy',
        pattern: '*_ProteinQuantifier_peptide.csv'

    publishDir "${params.process_log_dir}/${task.process.replace(':', '/')}-${task.index}/",
        mode: 'copy',
        pattern: '.command.*',
        saveAs: { "log${file(it).name}" }

    input:
        tuple path(peptide_raw), path(consensusXML)

    output:
        path peptide_out
        path '.command.*'

    script:
    peptide_out = "${params.project_name}_ProteinQuantifier_peptide.csv"
    """
    python ${projectDir}/src/ReheaderProteinQuant.py \\
        --input-csv ${peptide_raw} \\
        --consensus-xml ${consensusXML} \\
        --output-csv ${peptide_out} \\
        --table peptide
    """
}
