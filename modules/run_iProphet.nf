/**
 * Nextflow module to run iProphet that merges multiple pepXML into one.
 */
process run_iProphet {
    container params.docker_image_fragpipe

    publishDir "${params.intermediate_file_dir}/${task.process.replace(':', '/')}/",
        mode: 'copy',
        enabled: params.save_intermediate_files,
        pattern: '*.pepXML'

    publishDir "${params.process_log_dir}/${task.process.replace(':', '/')}/",
        mode: 'copy',
        pattern: '.command.*',
        saveAs: { "log${file(it).name}" }

    input:
        file input_pepxml
        file decoy_database

    output:
        file output_pepXML
        file ".command.*"

    script:
    output_prefix = "${params.project_name}_iProphet"
    output_pepXML = "${output_prefix}.pepXML"
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
    "\$philosopher_bin" iprophet \\
        --output ${output_prefix} \\
        --threads ${task.cpus} \\
        ${input_pepxml}
    mv ${output_prefix}.pep.xml ${output_pepXML}
    """
}
