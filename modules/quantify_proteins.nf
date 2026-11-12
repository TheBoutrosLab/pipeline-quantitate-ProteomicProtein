include { getOpenMSArgs } from "${moduleDir}/common"

PARAMETERS = []

FLAGS = []

PARAMETER_MAPPER = [
    'protein_quantifier_debug': '-debug',
    'protein_quantifier_top': '-top:N',
    'protein_quantifier_average': '-top:aggregate',
    'protein_quantifier_fractions_aggregate': '-fractions:aggregate',
    'protein_quantifier_consensus_normalize': '-consensus:normalize',
    'protein_quantifier_consensus_fix_peptides': '-consensus:fix_peptides',
    'protein_quantifier_greedy_group_resolution': '-greedy_group_resolution',
    'protein_quantifier_format_separator': '-format:separator',
    'protein_quantifier_format_quoting': '-format:quoting',
    'protein_quantifier_format_replacement': '-format:replacement'
]

FLAG_MAPPER = [
    'protein_quantifier_include_all': '-top:include_all',
    'protein_quantifier_best_charge': '-best_charge'
]

process quantify_proteins {
    container params.docker_image_openms

    publishDir "${params.intermediate_file_dir}/${task.process.replace(':', '/')}/",
        mode: 'copy',
        enabled: params.save_intermediate_files,
        pattern: "*_ProteinQuantifier_peptide_raw.csv"

    publishDir "${params.intermediate_file_dir}/${task.process.replace(':', '/')}/",
        mode: 'copy',
        enabled: params.save_intermediate_files,
        pattern: "*_ProteinQuantifier_protein_raw.csv"

    publishDir "${params.process_log_dir}/${task.process.replace(':', '/')}-${task.index}/",
        mode: 'copy',
        pattern: '.command.*',
        saveAs: { "log${file(it).name}" }

    input:
        file consensusXML
        file protein_groups

    output:
        tuple file(protein_out), file(peptide_out), file(consensusXML)
        file ".command.*"

    script:
    protein_out = "${params.project_name}_ProteinQuantifier_protein_raw.csv"
    peptide_out = "${params.project_name}_ProteinQuantifier_peptide_raw.csv"
    extra_args = getOpenMSArgs(PARAMETERS, FLAGS, PARAMETER_MAPPER, FLAG_MAPPER)
    if (protein_groups.name != 'NO_FILE') {
        extra_args += " -protein_groups ${protein_groups}"
    }

    """
    ProteinQuantifier \\
        -in ${consensusXML} \\
        -out ${protein_out} \\
        -peptide_out ${peptide_out} \\
        -threads ${task.cpus} \\
        ${extra_args}
    """
}
