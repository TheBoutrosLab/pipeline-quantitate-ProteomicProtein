""" Set database path of an idXML file
"""
import argparse
from pyopenms import IdXMLFile, PeptideIdentificationList


def parse_args():
    """ parse args """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input-path',
        type=str,
        help='Path to input idXML file.',
        required=True
    )
    parser.add_argument(
        '--database',
        type=str,
        help='Path to the database FASTA file.',
        required=True
    )
    parser.add_argument(
        '--output-path',
        type=str,
        help='Path to the output idXML file.',
        required=True
    )
    return parser.parse_args()

def main():
    """ main """
    args = parse_args()
    input_path:str = args.input_path
    output_path:str = args.output_path
    database:str = args.database

    peptides = PeptideIdentificationList()
    proteins = []

    IdXMLFile().load(input_path, proteins, peptides)

    for prot_ident in proteins:
        params = prot_ident.getSearchParameters()
        params.db = database
        prot_ident.setSearchParameters(params)

    IdXMLFile().store(output_path, proteins, peptides)


if __name__ == '__main__':
    main()
