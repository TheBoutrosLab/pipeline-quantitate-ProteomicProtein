/**
* This process sets the database path of an idXMl file.
*/
process set_databasePath {
    container params.docker_image_pyopenms
    containerOptions params.project_script_mount_options

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
        file database_fasta

    output:
        file output_idXML
        file ".command.*"

    script:
    output_idXML = "${input_idXML.baseName}_databaseFixed.idXML"
    """
    python ${projectDir}/src/IdXMLDatabasePathSetter.py \\
        --input-path ${input_idXML} \\
        --output-path ${output_idXML} \\
        --database ${database_fasta.toRealPath()}
    """
}
