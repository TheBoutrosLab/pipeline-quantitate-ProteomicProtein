/**
* Module for conversion from proteXML to idXML
*/
process convert_protXML2idXML {
    container params.docker_image_openms

    publishDir "${params.intermediate_file_dir}/${task.process.replace(':', '/')}/",
        mode: 'copy',
        enabled: params.save_intermediate_files,
        pattern: '*.idXML'

    publishDir "${params.process_log_dir}/${task.process.replace(':', '/')}/",
        mode: 'copy',
        pattern: '.command.*',
        saveAs: { "log${file(it).name}" }

    input:
        file protXML

    output:
        file idXML
        file '.command.*'

    script:
    idXML = "${protXML.baseName}.idXML"
    """
    IDFileConverter \\
        -in ${protXML} \\
        -out ${idXML}
    """
}
