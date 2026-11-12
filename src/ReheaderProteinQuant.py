"""Name OpenMS 3.6 protein assay columns from the quantified consensusXML."""

import argparse
import csv
import re
import shutil
from collections import defaultdict, OrderedDict
from pathlib import Path

from pyopenms import ConsensusMap, ConsensusXMLFile, ExperimentalDesign


ASSAY_COLUMN = re.compile(r'abundance_fgroup([1-9][0-9]*)_label([1-9][0-9]*)')
FILE_CHANNEL_COLUMN = re.compile(r'abundance\|(.+)\|ch([1-9][0-9]*)')


def text(value):
    """Convert pyOpenMS string values to Python text."""
    return value.decode() if isinstance(value, bytes) else str(value)


class ProteinQuantCSVReheader:
    """Keep the OpenMS design and quantification column mappings together."""

    def __init__(self, consensus_path: str):
        self.consensus_path = consensus_path
        self.consensus: ConsensusMap = None
        self.assays = OrderedDict()
        self.file_channels = {}

    def load_consensus(self):
        """Load the consensusXML when the caller is ready to process it."""
        self.consensus = ConsensusMap()
        ConsensusXMLFile().load(self.consensus_path, self.consensus)
        self.assays.clear()
        self.file_channels.clear()

    def build_column_names(self):
        """Name each assay using OpenMS's fraction group and label identifiers."""
        if self.consensus is None:
            raise ValueError('Load the consensusXML before building column names')

        self.file_channels.clear()
        design = ExperimentalDesign.fromConsensusMap(self.consensus)
        by_path_label = defaultdict(list)
        for header in self.consensus.getColumnHeaders().values():
            filename = text(header.filename)
            label = (int(header.getMetaValue('channel_id')) + 1
                     if header.metaValueExists('channel_id') else 1)
            by_path_label[(filename, label)].append(header)
            description = (text(header.getMetaValue('channel_description')).strip()
                           if header.metaValueExists('channel_description') else '')
            file_channel = (Path(filename).stem, label)
            existing = self.file_channels.get(file_channel, '')
            if existing and description and existing != description:
                raise ValueError(f'File/channel {file_channel} has conflicting descriptions')
            self.file_channels[file_channel] = existing or description

        grouped = OrderedDict()
        for entry in design.getMSFileSection():
            assay = (int(entry.fraction_group), int(entry.label))
            source = text(entry.path)
            matching = [header for header in by_path_label.get((source, assay[1]), [])
                        if not header.metaValueExists('fraction_group')
                        or int(header.getMetaValue('fraction_group')) == assay[0]]
            if not matching:
                raise ValueError(f'No consensusXML map matches assay {assay} and file {source!r}')
            grouped.setdefault(assay, []).append((entry, matching))

        if not grouped:
            raise ValueError('ConsensusXML contains no quantified assays')

        self.assays.clear()
        for assay, rows in grouped.items():
            filenames = {text(header.filename) for _, matching in rows for header in matching}
            sample_names = {text(entry.sample_name) for entry, _ in rows}
            if len(filenames) == 1:
                name = next(iter(filenames))
            elif (len(sample_names) == 1 and
                  any(header.metaValueExists('sample_name')
                      for _, matching in rows for header in matching)):
                name = next(iter(sample_names))
            else:
                name = f'fgroup{assay[0]}'
            if not name or '\t' in name or '|' in name:
                raise ValueError(f'Assay {assay} has an unusable name {name!r}')

            descriptions = {text(header.getMetaValue('channel_description')).strip()
                            for _, matching in rows for header in matching
                            if header.metaValueExists('channel_description')
                            and text(header.getMetaValue('channel_description')).strip()}
            if len(descriptions) > 1:
                raise ValueError(f'Assay {assay} has conflicting channel descriptions')
            name = f'abundance|{name}|ch{assay[1]}'
            if descriptions:
                description = next(iter(descriptions))
                if '\t' in description or '|' in description:
                    raise ValueError(f'Assay {assay} has an unusable channel description')
                name += f'|{description}'
            self.assays[assay] = name

        duplicates = defaultdict(list)
        for assay, name in self.assays.items():
            duplicates[name].append(assay)
        for name, assays in duplicates.items():
            if len(assays) > 1:
                for assay in assays:
                    self.assays[assay] = f'{name}|fgroup{assay[0]}'
        return self.assays

    def replace_header(self, line: str, table: str = 'protein'):
        """Replace assay or detailed peptide headers without changing their order."""
        if not self.assays:
            raise ValueError('Build column names before rewriting the CSV')
        if '\t' not in line:
            raise ValueError('Expected tab-separated ProteinQuantifier output')

        header = next(csv.reader([line], delimiter='\t'))
        seen = set()
        detailed = False
        for index, name in enumerate(header):
            match = ASSAY_COLUMN.fullmatch(name)
            if match:
                assay = (int(match.group(1)), int(match.group(2)))
                if assay not in self.assays or assay in seen:
                    raise ValueError(f'Unexpected or repeated protein abundance assay {assay}')
                header[index] = self.assays[assay]
                seen.add(assay)
            elif table == 'peptide' and (match := FILE_CHANNEL_COLUMN.fullmatch(name)):
                detailed = True
                file_channel = (match.group(1), int(match.group(2)))
                if file_channel not in self.file_channels:
                    raise ValueError(f'Unknown peptide abundance file/channel {file_channel}')
                description = self.file_channels[file_channel]
                if description:
                    header[index] = f'{name}|{description}'
            elif name.startswith('abundance'):
                raise ValueError(f'Unexpected {table} abundance header {name!r}')
        if detailed and seen:
            raise ValueError('Peptide output mixes assay and file/channel abundance columns')
        if not detailed and seen != self.assays.keys():
            raise ValueError(f'ProteinQuantifier is missing assays {set(self.assays) - seen}')
        return header

    def write(self, input_path, output_path, table: str = 'protein'):
        """Rewrite only the header line; copy comments and protein rows verbatim."""
        if not self.assays:
            raise ValueError('Build column names before rewriting the CSV')
        with open(input_path, encoding='utf-8', newline='') as source, \
                open(output_path, 'w', encoding='utf-8', newline='') as target:
            for line in source:
                if line.startswith('#'):
                    target.write(line)
                    continue
                header = self.replace_header(line, table)
                writer = csv.writer(target, delimiter='\t', lineterminator='\n')
                writer.writerow(header)
                shutil.copyfileobj(source, target)
                return
        raise ValueError('ProteinQuantifier output has no table header')


def main():
    """Parse command-line inputs and write the renamed quantification table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-csv', required=True)
    parser.add_argument('--consensus-xml', required=True)
    parser.add_argument('--output-csv', required=True)
    parser.add_argument('--table', choices=('protein', 'peptide'), default='protein')
    args = parser.parse_args()
    reheader = ProteinQuantCSVReheader(args.consensus_xml)
    reheader.load_consensus()
    reheader.build_column_names()
    reheader.write(args.input_csv, args.output_csv, args.table)


if __name__ == '__main__':
    main()
