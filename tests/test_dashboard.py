import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import dashboard

class DashboardTests(unittest.TestCase):
    def sample(self):
        return {'tier':'fixture','upstreamExecuted':False,'id':'test','environment':'synthetic <script>',
                'contractTests':{'status':'passed'},'sources':[], 'runs':[]}

    def test_escapes_labels_and_retains_blockers(self):
        result = dashboard.render(self.sample())
        self.assertIn('&lt;script&gt;', result)
        self.assertNotIn('synthetic <script>', result)
        self.assertIn('Full integration not implemented', result)

    def test_rejects_product_promotion(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); sample=self.sample(); sample['upstreamExecuted']=True
            (root/'summary.json').write_text(json.dumps(sample))
            with self.assertRaises(ValueError): dashboard.build(root/'summary.json', root/'site')

    def test_rejects_media_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); sample=self.sample();sample['runs']=[{'media':[{'path':'../secret','sha256':'x'}]}]
            (root/'summary.json').write_text(json.dumps(sample))
            with self.assertRaises(ValueError): dashboard.build(root/'summary.json', root/'site')

    def test_rejects_tampered_media(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); sample=self.sample();sample['runs']=[{'media':[{'path':'clip.webm','sha256':'x'}]}]
            (root/'clip.webm').write_bytes(b'altered');(root/'summary.json').write_text(json.dumps(sample))
            with self.assertRaises(ValueError): dashboard.build(root/'summary.json', root/'site')
