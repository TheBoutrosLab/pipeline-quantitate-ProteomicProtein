/**
 * Correct enzyme-specific termini in OpenMS-exported pepXML before iProphet.
 */
process fix_pepxml_termini {
    container params.docker_image_fragpipe
    containerOptions "-v ${projectDir}/src/:${projectDir}/src/"

    publishDir "${params.intermediate_file_dir}/${task.process.replace(':', '/')}/",
        mode: 'copy',
        enabled: params.save_intermediate_files,
        pattern: '*.pepXML'

    publishDir "${params.process_log_dir}/${task.process.replace(':', '/')}-${task.index}/",
        mode: 'copy',
        pattern: '.command.*',
        saveAs: { "log${file(it).name}" }

    input:
        file input_pepXML

    output:
        file output_pepXML
        file '.command.*'

    script:
    output_pepXML = "${input_pepXML.baseName}_terminiFixed.pepXML"
    """
    python3 ${projectDir}/src/FixPepXMLTermini.py \\
        --input-path ${input_pepXML} \\
        --output-path ${output_pepXML}
    """
}
