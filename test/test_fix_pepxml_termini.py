"""Check enzyme termini and PEP probabilities in repaired pepXML."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

try:
    from lxml import etree
except ImportError:
    etree = None


@unittest.skipUnless(etree is not None, 'lxml is required')
class FixPepXMLTerminiTest(unittest.TestCase):
    """Test a small pepXML with different protein-match termini."""

    @classmethod
    def setUpClass(cls):
        script = Path(__file__).resolve().parents[1] / 'src' / 'FixPepXMLTermini.py'
        spec = importlib.util.spec_from_file_location('fix_pepxml_termini', script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.repair_file = staticmethod(module.repair_file)

    def test_recalculates_each_match_and_preserves_pep(self):
        xml = '''<?xml version="1.0"?>
<msms_pipeline_analysis xmlns="http://regis-web.systemsbiology.net/pepXML">
 <msms_run_summary>
  <sample_enzyme name="trypsin/p"><specificity cut="KR" no_cut="" sense="C"/></sample_enzyme>
  <spectrum_query><search_result>
   <search_hit peptide="PEPTIDER" peptide_prev_aa="K" peptide_next_aa="A" num_tol_term="1">
    <alternative_protein protein="B" peptide_prev_aa="A" peptide_next_aa="P" num_tol_term="1"/>
    <analysis_result>
     <peptideprophet_result probability="0.97" all_ntt_prob="(0,0,0.97)"/>
    </analysis_result>
   </search_hit>
  </search_result></spectrum_query>
 </msms_run_summary>
</msms_pipeline_analysis>'''
        with TemporaryDirectory() as temp:
            source = Path(temp) / 'input.pepXML'
            output = Path(temp) / 'output.pepXML'
            source.write_text(xml)
            self.repair_file(str(source), str(output))
            root = etree.parse(str(output))
        namespace = {'p': 'http://regis-web.systemsbiology.net/pepXML'}
        hit = root.find('.//p:search_hit', namespace)
        self.assertEqual(hit.get('num_tol_term'), '2')
        self.assertEqual(hit.find('p:alternative_protein', namespace).get('num_tol_term'), '1')
        probability = hit.find('p:analysis_result/p:peptideprophet_result', namespace)
        self.assertEqual(probability.get('probability'), '0.97')
        self.assertEqual(probability.get('all_ntt_prob'), '(0.97,0.97,0.97)')


if __name__ == '__main__':
    unittest.main()
