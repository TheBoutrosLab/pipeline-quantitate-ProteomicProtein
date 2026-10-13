""" This module takes in the idXML file converted from a protXML output by
ProteinProphet and filters protein groups (indistinguishable proteins) with
a given cutoff of probability. The motivation is that ProteinProphet usually
assign a leader protein to a group of indistinguishable proteins. But it also
reports "unneeded" proteins with probability of zero. Including those protein
groups in the idXML file confuses ProteinQuantifier for not being able to use
shared peptides to quantitate the correct protein (group).
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

def main():
    """ main """
    args = parse_args()

    prot_idents = []
    pep_idents = PeptideIdentificationList()
    IdXMLFile().load(args.input_path, prot_idents, pep_idents)

    new_prot_idents = create_protein_identification(prot_idents[0])

    if args.grouping_algorithm == 'ProteinProphet':
        protein_groups = prot_idents[0].getProteinGroups()
    else:
        protein_groups = prot_idents[0].getIndistinguishableProteins()

    for pg in protein_groups:
        if pg.probability <= args.probability_cutoff:
            continue
        new_prot_idents.insertProteinGroup(pg)
        new_prot_idents.insertIndistinguishableProteins(pg)

    IdXMLFile().store(args.output_path, [new_prot_idents], pep_idents)


if __name__ == '__main__':
    main()
