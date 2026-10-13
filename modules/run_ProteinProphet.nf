/**
 * Nextflow module to call ProteinProphet for protein grouping.
 */

include { getPhilosopherArgs } from "${moduleDir}/common"

PARAMETERS = []

FLAGS = []

PARAMETER_MAPPER = [
    'proteinprophet_minprob': '--minprob',
    'proteinprophet_maxppmdiff': '--maxppmdiff',
]

FLAG_MAPPER = [
    'proteinprophet_nonsp': '--nonsp',
    'proteinprophet_unmapped': '--unmapped'
]

process run_ProteinProphet {
    container params.docker_image_fragpipe

    publishDir "${params.intermediate_file_dir}/${task.process.replace(':', '/')}/",
        mode: 'copy',
        enabled: params.save_intermediate_files,
        pattern: '*_PeptideProphet.protXML'

    publishDir "${params.process_log_dir}/${task.process.replace(':', '/')}/",
        mode: 'copy',
        pattern: '.command.*',
        saveAs: { "log${file(it).name}" }

    input:
        file input_pepxml
        file decoy_database

    output:
        file output_protXML
        file ".command.*"

    script:
    output_prefix = "${params.project_name}_ProteinProphet"
    output_protXML = "${output_prefix}.protXML"
    extra_args = getPhilosopherArgs(PARAMETERS, FLAGS, PARAMETER_MAPPER, FLAG_MAPPER)
    """
    set -euo pipefail
    philosopher_bin=''
    for candidate in /fragpipe_bin/fragpipe-24.0/fragpipe-24.0/tools/Philosopher/philosopher*; do
        if [ -f "\$candidate" ] && [ -x "\$candidate" ]; then
            philosopher_bin="\$candidate"
            break
        fi
    done
    if [ -z "\$philosopher_bin" ]; then
        echo 'Philosopher executable not found in the configured FragPipe image' >&2
        exit 127
    fi
    "\$philosopher_bin" workspace --init
    "\$philosopher_bin" database --annotate ${decoy_database} --prefix ${params.decoy_string}
    "\$philosopher_bin" proteinprophet \\
        ${extra_args} \\
        --output ${output_prefix} \\
        --iprophet \\
        ${input_pepxml}
    mv ${output_prefix}.prot.xml ${output_protXML}
    """
}
