/** Label sample-level protein abundances using the quantified consensusXML. */
process reheader_ProteinQuantCSV {
    container params.docker_image_pyopenms
    containerOptions params.project_script_mount_options

    publishDir params.final_output_dir,
        mode: 'copy',
        pattern: '*_ProteinQuantifier_protein.csv'

    publishDir "${params.process_log_dir}/${task.process.replace(':', '/')}-${task.index}/",
        mode: 'copy',
        pattern: '.command.*',
        saveAs: { "log${file(it).name}" }

    input:
        tuple path(protein_raw), path(consensusXML)

    output:
        path protein_out
        path '.command.*'

    script:
    protein_out = "${params.project_name}_ProteinQuantifier_protein.csv"
    """
    python ${projectDir}/src/ReheaderProteinQuant.py \\
        --input-csv ${protein_raw} \\
        --consensus-xml ${consensusXML} \\
        --output-csv ${protein_out}
    """
}
