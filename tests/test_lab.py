import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('lab', ROOT / 'tools/lab.py')
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class LabTests(unittest.TestCase):
    def test_all_case_tiers_fail_closed(self):
        for case in lab.CASES:
            for tier in lab.TIERS:
                result = lab.blocked(case, tier)
                self.assertEqual(result['status'], 'blocked')
                self.assertFalse(result['productAcceptance'])
                self.assertIsNone(result['measurements'])
                self.assertEqual(result['media'], [])

    def test_unknown_tier_rejected(self):
        with self.assertRaises(ValueError):
            lab.blocked('bakery-prep', 'fallback')

    def test_actual_gitlinks_match(self):
        self.assertEqual(len(lab.check()), 2)

    def test_pin_mutation_rejected(self):
        original = lab.git
        def altered(*args, **kwargs):
            if args[:2] == ('ls-files', '--stage'):
                return '160000 ' + '0' * 40 + ' 0 sources/runspindle'
            return original(*args, **kwargs)
        with patch.object(lab, 'git', side_effect=altered):
            with self.assertRaises(ValueError):
                lab.check()

    def test_report_keeps_blockers_and_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(lab, 'check', return_value=[]), patch.object(lab, 'git', return_value=''):
                out = lab.report(Path(tmp))
            data = json.loads((out / 'status.json').read_text())
            self.assertEqual(len(data['runs']), 6)
            self.assertTrue(all(x['status'] == 'blocked' for x in data['runs']))
            for name, digest in json.loads((out / 'sha256.json').read_text()).items():
                self.assertEqual(hashlib.sha256((out / name).read_bytes()).hexdigest(), digest)

    def test_cli_product_is_non_success(self):
        p = subprocess.run(['python3', 'tools/lab.py', 'run', '--tier', 'product'],
                           cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(p.returncode, 78)
        self.assertEqual(json.loads(p.stdout)['tier'], 'product')


if __name__ == '__main__':
    unittest.main()
