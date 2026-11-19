/**
 * Correct enzyme-specific termini in OpenMS-exported pepXML before iProphet.
 */
process fix_pepxml_termini {
    container params.docker_image_fragpipe
    containerOptions params.project_script_mount_options

    publishDir "${params.intermediate_file_dir}/${task.process.replace(':', '/')}/",
        mode: 'copy',
        enabled: params.save_intermediate_files,
        pattern: '*.pepXML'

    publishDir "${params.process_log_dir}/${task.process.replace(':', '/')}-${task.index}/",
        mode: 'copy',
        pattern: '.command.*',
        saveAs: { "log${file(it).name}" }

    input:
        tuple file(input_pepXML), file(enzyme_rule_json)

    output:
        file output_pepXML
        file '.command.*'

    script:
    output_pepXML = "${input_pepXML.baseName}_terminiFixed.pepXML"
    """
    python3 ${projectDir}/src/FixPepXMLTermini.py \\
        --input-path ${input_pepXML} \\
        --enzyme-rule-path ${enzyme_rule_json} \\
        --output-path ${output_pepXML}
    """
}
