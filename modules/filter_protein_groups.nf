/**
* This process filters off the protein groups called by ProteinProphet according to the probability.
*/
process filter_protein_groups {
    container params.docker_image_pyopenms
    containerOptions "-v ${projectDir}/src/:${projectDir}/src/"

    publishDir params.final_output_dir,
        mode: 'copy',
        pattern: "${params.project_name}_ProteinProphet_filtered.idXML"

    publishDir "${params.intermediate_file_dir}/${task.process.replace(':', '/')}/",
        mode: 'copy',
        enabled: params.save_intermediate_files,
        pattern: '*.idXML'

    publishDir "${params.process_log_dir}/${task.process.replace(':', '/')}-${task.index}/",
        mode: 'copy',
        pattern: '.command.*',
        saveAs: { "log${file(it).name}" }

    input:
        file input_idXML

    output:
        file output_idXML
        file ".command.*"

    script:
    output_idXML = "${params.project_name}_ProteinProphet_filtered.idXML"
    """
    python ${projectDir}/src/FilterProteinGroups.py \\
        --input-path ${input_idXML} \\
        --output-path ${output_idXML} \\
        --probability-cutoff 0 \\
        --grouping-algorithm ProteinProphet
    """
}
