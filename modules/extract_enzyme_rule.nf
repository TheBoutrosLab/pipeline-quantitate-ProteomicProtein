/** Extract the OpenMS digestion enzyme rule from idXML for pepXML repair. */
process extract_enzyme_rule {
    container params.docker_image_pyopenms
    containerOptions params.project_script_mount_options

    publishDir "${params.intermediate_file_dir}/${task.process.replace(':', '/')}/",
        mode: 'copy',
        enabled: params.save_intermediate_files,
        pattern: '*.json'

    publishDir "${params.process_log_dir}/${task.process.replace(':', '/')}-${task.index}/",
        mode: 'copy',
        pattern: '.command.*',
        saveAs: { "log${file(it).name}" }

    input:
        file input_idXML

    output:
        tuple file(input_idXML), file(enzyme_rule_json)
        file '.command.*'

    script:
    enzyme_rule_json = "${input_idXML.baseName}_enzymeRule.json"
    """
    python ${projectDir}/src/ExtractEnzymeRule.py \\
        --input-path ${input_idXML} \\
        --output-path ${enzyme_rule_json}
    """
}
