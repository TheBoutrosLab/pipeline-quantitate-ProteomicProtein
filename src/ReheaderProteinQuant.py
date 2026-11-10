"""Name OpenMS sample-level protein columns from the quantified consensusXML."""

import argparse
import csv
import re
import shutil
from collections import OrderedDict

from pyopenms import ConsensusMap, ConsensusXMLFile


SAMPLE_COLUMN = re.compile(r'abundance_sample([1-9][0-9]*)\[[^\]]*\]')


def text(value):
    """Convert pyOpenMS string values to Python text."""
    return value.decode() if isinstance(value, bytes) else str(value)


class ProteinQuantCSVReheader:
    """Keep the OpenMS map and its sample-to-column mapping together."""

    def __init__(self, consensus_path: str):
        self.consensus_path:str = consensus_path
        self.consensus:ConsensusMap = None
        self.filenames = OrderedDict()
        self.samples = OrderedDict()
        self.column_names: list[str] = []

    def load_consensus(self):
        """Load the consensusXML when the caller is ready to process it."""
        self.consensus = ConsensusMap()
        ConsensusXMLFile().load(self.consensus_path, self.consensus)
        self.filenames.clear()
        self.samples.clear()
        self.column_names = []

    def build_column_names(self):
        """Follow OpenMS 3.5 ExperimentalDesign::fromConsensusMap sample ordering."""
        if self.consensus is None:
            raise ValueError('Load the consensusXML before building protein column names')

        self.filenames.clear()
        self.samples.clear()
        self.column_names = []

        headers = self.consensus.getColumnHeaders()

        if sorted(headers) != list(range(len(headers))):
            raise ValueError('ConsensusXML map IDs must be consecutive from zero')

        for map_id, header in sorted(headers.items()):
            filename = text(header.filename)
            if not filename or '\t' in filename or '|' in filename:
                raise ValueError(f'Map {map_id} has an unusable filename {filename!r}')
            label = (int(header.getMetaValue('channel_id')) + 1
                     if header.metaValueExists('channel_id') else 1)
            if label < 1:
                raise ValueError(f'Map {map_id} has an invalid channel_id')
            if header.metaValueExists('fraction'):
                if not header.metaValueExists('fraction_group'):
                    raise ValueError(f'Map {map_id} has a fraction without fraction_group')
                group = int(header.getMetaValue('fraction_group'))
            else:
                self.filenames.setdefault(filename, len(self.filenames) + 1)
                group = self.filenames[filename]
            key = (('sample_name', text(header.getMetaValue('sample_name')))
                   if header.metaValueExists('sample_name') else (group, label))
            description = (text(header.getMetaValue('channel_description')).strip()
                           if header.metaValueExists('channel_description') else '')
            self.samples.setdefault(key, []).append((filename, label, description))

        if not self.samples:
            raise ValueError('ConsensusXML contains no map headers')

        names: list[str] = []
        for key, members in self.samples.items():
            labels = {label for _, label, _ in members}

            if len(labels) != 1:
                raise ValueError(f'Sample {key!r} spans multiple reporter channels')

            source_names = {filename for filename, _, _ in members}

            if len(source_names) == 1:
                sample_name = members[0][0]
            elif key[0] == 'sample_name':
                sample_name = key[1]
            else:
                raise ValueError(f'Sample {key!r} spans multiple filenames without a sample_name')

            if not sample_name or '\t' in sample_name or '|' in sample_name:
                raise ValueError(f'Sample {key!r} has an unusable name')

            descriptions = {description for _, _, description in members if description}
            if len(descriptions) > 1:
                raise ValueError(f'Sample {key!r} has conflicting channel descriptions')
            name = f'abundance|{sample_name}|ch{members[0][1]}'
            if descriptions:
                description = next(iter(descriptions))
                if '\t' in description or '|' in description:
                    raise ValueError(f'Sample {key!r} has an unusable channel description')
                name += f'|{description}'
            names.append(name)

        if len(names) != len(set(names)):
            raise ValueError('ConsensusXML samples produce duplicate abundance headers')

        self.column_names = names
        return names

    def replace_header(self, line: str):
        """Validate OpenMS sample numbers before assigning map-derived names."""
        if not self.column_names:
            raise ValueError('Build protein column names before rewriting the CSV')
        if '\t' not in line:
            raise ValueError('Expected tab-separated ProteinQuantifier output')

        header = next(csv.reader([line], delimiter='\t'))
        abundance_indices = [
            i for i, name in enumerate(header)
            if name == 'abundance' or name.startswith('abundance_sample')
        ]

        if not abundance_indices:
            raise ValueError('ProteinQuantifier output has no sample abundance columns')

        if len(abundance_indices) != len(self.column_names):
            raise ValueError(f'ProteinQuantifier has {len(abundance_indices)} sample columns; '
                             f'consensusXML defines {len(self.column_names)} samples')

        if abundance_indices != list(range(abundance_indices[0], abundance_indices[-1] + 1)):
            raise ValueError('Protein abundance columns are not consecutive')

        actual = [header[i] for i in abundance_indices]
        if len(self.column_names) == 1:
            if actual != ['abundance']:
                raise ValueError(f'Unexpected single-sample abundance header: {actual}')
        else:
            matches = [SAMPLE_COLUMN.fullmatch(value) for value in actual]
            if any(match is None for match in matches):
                raise ValueError(f'Unexpected protein abundance headers: {actual}')
            if [int(match.group(1)) for match in matches] != list(range(1, len(matches) + 1)):
                raise ValueError('Protein abundance sample numbers are out of order')

        for index, name in zip(abundance_indices, self.column_names):
            header[index] = name

        return header

    def write(self, input_path, output_path):
        """Rewrite only the header line; copy comments and protein rows verbatim."""
        if not self.column_names:
            raise ValueError('Build protein column names before rewriting the CSV')
        with open(input_path, encoding='utf-8', newline='') as source, \
                open(output_path, 'w', encoding='utf-8', newline='') as target:
            for line in source:
                if line.startswith('#'):
                    target.write(line)
                    continue
                header = self.replace_header(line)
                writer = csv.writer(target, delimiter='\t', lineterminator='\n')
                writer.writerow(header)
                shutil.copyfileobj(source, target)
                return
        raise ValueError('ProteinQuantifier output has no table header')


def main():
    """Parse command-line inputs and write the renamed protein table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-csv', required=True)
    parser.add_argument('--consensus-xml', required=True)
    parser.add_argument('--output-csv', required=True)
    args = parser.parse_args()
    reheader = ProteinQuantCSVReheader(args.consensus_xml)
    reheader.load_consensus()
    reheader.build_column_names()
    reheader.write(args.input_csv, args.output_csv)


if __name__ == '__main__':
    main()
