include { getOpenMSArgs } from "${moduleDir}/common"

PARAMETERS = [

]

FLAGS = [

]

PARAMETER_MAPPER = [
    'filter_protein_precursor_rt': '-precursor:rt',
    'filter_protein_precursor_mz': '-precursor:mz',
    'filter_protein_precursor_length': '-precursor:length',
    'filter_protein_precursor_charge': '-precursor:charge',

    'filter_protein_score_pep': '-score:peptide',
    'filter_protein_score_prot': '-score:protein',
    'filter_protein_score_protgroup': '-score:proteingroup',

    'filter_protein_whitelist_proteins': '-whitelist:proteins',
    'filter_protein_whitelist_protein_accessions': '-whitelist:protein_accessions',
    'filter_protein_whitelist_peptides': '-whitelist:peptides',

    'filter_protein_blacklist_proteins': '-blacklist:proteins',
    'filter_protein_blacklist_protein_accessions': '-blacklist:protein_accessions',
    'filter_protein_blacklist_peptides': '-blacklist:peptides',

    'filter_protein_in_silico_digestion_fasta': '-in_silico_digestion:fasta',

    'filter_protein_missed_cleavages_number_of_missed_cleavages': '-missed_cleavages:number_of_missed_cleavages',

    'filter_protein_best_n_spectra': '-best:n_spectra',
    'filter_protein_best_n_peptide_hits': '-best:n_peptide_hits',
    'filter_protein_best_n_protein_hits': '-best:n_protein_hits'
]

FLAG_MAPPER = [
    'filter_protein_best_strict': '-best:strict',
    'filter_protein_var_mods': '-var_mods',
    'filter_protein_remove_shared_peptides': '-remove_shared_peptides',
    'filter_protein_keep_unreferenced_protein_hits': '-keep_unreferenced_protein_hits',
    'filter_protein_remove_decoys': '-remove_decoys'
]

process filter_proteins {
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
    output_file = "${params.project_name}_filtered.consensusXML"
    extra_args = getOpenMSArgs(PARAMETERS, FLAGS, PARAMETER_MAPPER, FLAG_MAPPER)
    """
    IDFilter \\
        -in ${consensusXML} \\
        -out ${output_file} \\
        -threads ${task.cpus} \\
        -score:protein ${params.protein_fdr_cutoff} \\
        -delete_unreferenced_peptide_hits \\
        ${extra_args}
    """
}
