"""Check that filtering preserves distinct parent and indistinguishable groups."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


class Group:
    """Minimal ProteinGroup stand-in."""

    def __init__(self, probability, accessions):
        self.probability = probability
        self.accessions = accessions


class Proteins:
    """Minimal ProteinIdentification stand-in."""

    def __init__(self, parents=(), indistinguishable=()):
        self.parents = list(parents)
        self.indistinguishable = list(indistinguishable)

    def getProteinGroups(self):  # pylint: disable=invalid-name
        return self.parents

    def getIndistinguishableProteins(self):  # pylint: disable=invalid-name
        return self.indistinguishable

    def insertProteinGroup(self, group):  # pylint: disable=invalid-name
        self.parents.append(group)

    def insertIndistinguishableProteins(self, group):  # pylint: disable=invalid-name
        self.indistinguishable.append(group)


class FilterGroupsTest(unittest.TestCase):
    """Exercise the shared filter used by ProteinProphet and future Fido input."""

    @classmethod
    def setUpClass(cls):
        script = Path(__file__).resolve().parents[1] / 'src' / 'FilterProteinGroups.py'
        spec = importlib.util.spec_from_file_location('filter_protein_groups', script)
        pyopenms_stub = types.ModuleType('pyopenms')
        pyopenms_stub.IdXMLFile = object
        pyopenms_stub.PeptideIdentificationList = list
        pyopenms_stub.ProteinIdentification = Proteins
        with patch.dict(sys.modules, {'pyopenms': pyopenms_stub}):
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        cls.filter_groups = staticmethod(module.filter_groups)

    def test_preserves_subgroups_for_both_algorithms(self):
        for algorithm in ('ProteinProphet', 'Fido'):
            with self.subTest(algorithm=algorithm):
                parent = Group(0.95, ['A', 'B', 'C'])
                ab = Group(0.95, ['A', 'B'])
                c = Group(0.95, ['C'])
                removed = Group(0.0, ['D'])
                source = Proteins([parent, removed], [ab, c, Group(0.0, ['D'])])
                output = Proteins()

                self.filter_groups(source, 0, output, algorithm)

                self.assertEqual(output.parents, [parent])
                self.assertEqual(output.indistinguishable, [ab, c])

    def test_rejects_partly_filtered_indistinguishable_group(self):
        source = Proteins(
            [Group(0.95, ['A']), Group(0.0, ['B'])],
            [Group(0.95, ['A', 'B'])],
        )
        with self.assertRaisesRegex(ValueError, 'spans retained and filtered'):
            self.filter_groups(source, 0, Proteins(), 'Fido')


if __name__ == '__main__':
    unittest.main()
