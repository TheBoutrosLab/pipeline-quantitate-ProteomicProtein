include { getOpenMSArgs } from "${moduleDir}/common"

PARAMETERS = [

]

FLAGS = [

]

PARAMETER_MAPPER = [
    'protein_inference_merge_runs': '-merge_runs',
    'protein_inference_protein_fdr': '-protein_fdr',
    'protein_inference_picked_fdr': '-picked_fdr',
    'protein_inference_decoy_string': '-picked_decoy_string',
    'protein_inference_decoy_string_prefix': '-picked_decoy_prefix',
    'protein_inference_Merging_annotate_origin': '-Merging:annotate_origin',
    'protein_inference_Algorithm_min_peptides_per_protein': '-Algorithm:min_peptides_per_protein',
    'protein_inference_Algorithm_score_aggregation_method': '-Algorithm:score_aggregation_method',
    'protein_inference_Algorithm_treat_charge_variants_separately': '-Algorithm:treat_charge_variants_separately',
    'protein_inference_Algorithm_treat_modification_variants_separately': '-Algorithm:treat_modification_variants_separately',
    'protein_inference_Algorithm_use_shared_peptides': '-Algorithm:use_shared_peptides',
    'protein_inference_Algorithm_annotate_indistinguishable_groups': '-Algorithm:annotate_indistinguishable_groups'
]

FLAG_MAPPER = [
    'protein_inference_Merging_allow_disagreeing_settings': '-Merging:allow_disagreeing_settings',
    'protein_inference_Algorithm_skip_count_annotation': '-Algorithm:skip_count_annotation',
    'protein_inference_Algorithm_greedy_group_resolution': '-Algorithm:greedy_group_resolution'
]

process infer_proteins {
    container params.docker_image_openms

    publishDir "${params.intermediate_file_dir}/${task.process.replace(':', '/')}/",
        mode: 'copy',
        enabled: params.save_intermediate_files,
        pattern: "*.consensusXML"

    publishDir "${params.process_log_dir}/${task.process.replace(':', '/')}-${task.index}/",
        mode: 'copy',
        pattern: '.command.*',
        saveAs: { "log${file(it).name}" }

    input:
        file consensusXML

    output:
        file output_file
        file ".command.*"

    script:
    output_file = "${params.project_name}_ProteinInference.consensusXML"
    extra_args = getOpenMSArgs(PARAMETERS, FLAGS, PARAMETER_MAPPER, FLAG_MAPPER)
    """
    ProteinInference \\
        -in ${consensusXML} \\
        -out ${output_file} \\
        -threads ${task.cpus} \\
        ${extra_args}
    """
}
