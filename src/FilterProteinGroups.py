"""Filter protein groups by probability in an inference idXML file.

Preserve the input's separate parent and indistinguishable group collections.
ProteinProphet may assign zero probability to proteins whose peptides are
explained by other proteins in the same parent group.
"""
import argparse
from pyopenms import IdXMLFile, PeptideIdentificationList, ProteinIdentification

def parse_args() -> argparse.Namespace:
    """ parse args """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input-path',
        type=str,
        help='Path to the input idXML file.',
        required=True
    )
    parser.add_argument(
        '-o', '--output-path',
        type=str,
        help='Path to the output idXML file.',
        required=True
    )
    parser.add_argument(
        '--probability-cutoff',
        type=float,
        help='Probability cutoff for filtering. Protein groups with probability'
        'smaller or equal to this value will be removed.',
        required=True
    )
    parser.add_argument(
        '--grouping-algorithm',
        type=str,
        choices=['ProteinProphet', 'Fido'],
        help='Protein grouping algorithm used.',
        required=True
    )
    return parser.parse_args()

def create_protein_identification(proteins:ProteinIdentification) -> ProteinIdentification:
    """ Creates a new protein identification based on a given one. """
    new_proteins = ProteinIdentification()
    new_proteins.setHits(proteins.getHits())
    new_proteins.setScoreType(proteins.getScoreType())
    new_proteins.setSearchEngine(proteins.getSearchEngine())
    new_proteins.setSearchEngineVersion(proteins.getSearchEngineVersion())
    new_proteins.setSearchParameters(proteins.getSearchParameters())
    new_proteins.setSignificanceThreshold(proteins.getSignificanceThreshold())
    new_proteins.setIdentifier(proteins.getIdentifier())

    keys = []
    proteins.getKeys(keys)
    for key in keys:
        new_proteins.setMetaValue(key, proteins.getMetaValue(key))

    return new_proteins

def filter_groups(proteins: ProteinIdentification, cutoff: float,
        output: ProteinIdentification, algorithm: str):
    """Filter parent groups while preserving their indistinguishable subgroups."""
    parent_groups = proteins.getProteinGroups()
    indistinguishable_groups = proteins.getIndistinguishableProteins()
    print(
        f'Input groups: {len(parent_groups)} {algorithm} parent groups; '
        f'{len(indistinguishable_groups)} indistinguishable protein groups'
    )
    if not parent_groups or not indistinguishable_groups:
        raise ValueError(
            f'{algorithm} idXML lacks protein group data before filtering; '
            'inspect the input idXML.'
        )

    retained_parents = [group for group in parent_groups if group.probability > cutoff]
    if not retained_parents:
        raise ValueError(
            f'No {algorithm} parent groups exceed probability cutoff {cutoff}; '
            'cannot provide protein groups to ProteinQuantifier.'
        )

    retained_accessions = {
        accession
        for group in retained_parents
        for accession in group.accessions
    }
    retained_indistinguishable = []
    for group in indistinguishable_groups:
        accessions = set(group.accessions)
        if not accessions:
            raise ValueError(f'{algorithm} idXML contains an empty indistinguishable group.')
        if accessions <= retained_accessions:
            retained_indistinguishable.append(group)
        elif accessions & retained_accessions:
            raise ValueError(
                'An indistinguishable group spans retained and filtered '
                f'{algorithm} parent groups.'
            )

    if not retained_indistinguishable:
        raise ValueError(
            'No indistinguishable groups remain after filtering; '
            'inspect the input group memberships.'
        )

    for group in retained_parents:
        output.insertProteinGroup(group)
    for group in retained_indistinguishable:
        output.insertIndistinguishableProteins(group)
    print(
        f'Retained groups: {len(retained_parents)} {algorithm} parent groups; '
        f'{len(retained_indistinguishable)} indistinguishable protein groups'
    )


def main():
    """Filter groups while preserving their original subgroup structure."""
    args = parse_args()

    prot_idents: list[ProteinIdentification] = []
    pep_idents = PeptideIdentificationList()
    IdXMLFile().load(args.input_path, prot_idents, pep_idents)
    if len(prot_idents) != 1:
        raise ValueError(f'Expected one ProteinIdentification, found {len(prot_idents)}.')

    new_prot_idents = create_protein_identification(prot_idents[0])
    filter_groups(
        prot_idents[0], args.probability_cutoff, new_prot_idents,
        args.grouping_algorithm
    )

    IdXMLFile().store(args.output_path, [new_prot_idents], pep_idents)

    checked_proteins = []
    checked_peptides = PeptideIdentificationList()
    IdXMLFile().load(args.output_path, checked_proteins, checked_peptides)
    if not checked_proteins or not checked_proteins[0].getIndistinguishableProteins():
        raise ValueError('Filtered idXML has no indistinguishable groups after serialization.')


if __name__ == '__main__':
    main()
