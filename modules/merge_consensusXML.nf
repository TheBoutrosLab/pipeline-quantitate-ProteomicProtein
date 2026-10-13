/**
 * Module to merge consensusXMl files.
 */

process merge_consensusXML {
    container params.docker_image_openms

    publishDir "${params.intermediate_file_dir}/${task.process.replace(':', '/')}/",
        mode: 'copy',
        enabled: params.save_intermediate_files && params.protein_grouping_algorithm == 'ProteinInferencer',
        pattern: '*.consensusXML'

    publishDir params.final_output_dir,
        mode: 'copy',
        enabled: params.protein_grouping_algorithm != 'ProteinInferencer',
        pattern: "*.consensusXML"

    publishDir "${params.process_log_dir}/${task.process.replace(':', '/')}-${task.index}/",
        mode: 'copy',
        pattern: '.command.*',
        saveAs: { "log${file(it).name}" }

    input:
        file consensusXML

    output:
        file output_file
        file '.command.*'

    script:
    output_file = "${params.project_name}_merged.consensusXML"
    """
    FileMerger \\
        -in ${consensusXML} \\
        -in_type consensusXML \\
        -append_method 'append_cols' \\
        -out ${output_file} \\
        -threads ${task.cpus}
    """
}
