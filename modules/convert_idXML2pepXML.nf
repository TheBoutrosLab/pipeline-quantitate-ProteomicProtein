/**
* Module for convertion from idXML to pepXML
*/
include { getOpenMSArgs } from "${moduleDir}/common"

PARAMETERS = []

FLAGS = []

PARAMETER_MAPPER = [:]

FLAG_MAPPER = [
    'convert_idXML2pepXML_peptideprophet_analyzed': '-peptideprophet_analyzed'
]

process convert_idXML2pepXML {
    container params.docker_image_openms

    publishDir "${params.intermediate_file_dir}/${task.process.replace(':', '/')}/",
        mode: 'copy',
        enabled: params.save_intermediate_files,
        pattern: '*.pepXML'

    publishDir "${params.process_log_dir}/${task.process.replace(':', '/')}-${task.index}/",
        mode: 'copy',
        pattern: '.command.*',
        saveAs: { "log${file(it).name}" }

    input:
        file idxml_file

    output:
        file pepxml_file
        file '.command.*'

    script:
    pepxml_file = "${idxml_file.baseName}.pepXML"
    extra_args = getOpenMSArgs(PARAMETERS, FLAGS, PARAMETER_MAPPER, FLAG_MAPPER)
    """
    set -euo pipefail

    IDFileConverter \\
        -in ${idxml_file} \\
        -out ${pepxml_file} \\
        ${extra_args}
    """
}
