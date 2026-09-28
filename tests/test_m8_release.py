import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PY=ROOT/".venv"/"Scripts"/"python.exe"

class ReleaseCLITests(unittest.TestCase):
    def run_cli(self,*args):
        env=dict(os.environ); env["PYTHONPATH"]=str(ROOT/"src")
        return subprocess.run([str(PY),"-m","epv",*args],cwd=ROOT,text=True,capture_output=True,env=env)
    def test_verify_v1_json(self):
        p=self.run_cli("verify","examples/second_price.epl","--property","dsic","--json")
        self.assertEqual(p.returncode,0,p.stderr); self.assertEqual(json.loads(p.stdout)["assurance_level"],"V1")
    def test_verify_v2_json(self):
        p=self.run_cli("verify","examples/second_price.epl","--property","dsic","--assurance","v2","--backend","z3","--json")
        self.assertEqual(p.returncode,0,p.stderr); self.assertEqual(json.loads(p.stdout)["status"],"BOUNDED VERIFIED")
    def test_counterexample_write_and_replay(self):
        with tempfile.TemporaryDirectory() as d:
            cert=Path(d)/"counterexample.json"
            p=self.run_cli("verify","examples/first_price.epl","--property","dsic","--assurance","v2","--certificate-out",str(cert),"--json")
            self.assertEqual(p.returncode,2,p.stderr); self.assertTrue(cert.is_file())
            r=self.run_cli("replay",str(cert),"--source","examples/first_price.epl","--property","dsic","--json")
            self.assertEqual(r.returncode,0,r.stderr); self.assertEqual(json.loads(r.stdout)["status"],"PASS")
    def test_synthesis_and_repair(self):
        self.assertEqual(self.run_cli("synthesize").returncode,0)
        self.assertEqual(self.run_cli("repair").returncode,0)
    def test_doctor_reports_v3(self):
        p=self.run_cli("doctor"); self.assertEqual(p.returncode,0,p.stderr); self.assertTrue(json.loads(p.stdout)["v3_ready"])
    def test_representative_reproduction(self):
        env=dict(os.environ); env["PYTHONPATH"]=str(ROOT/"src")
        p=subprocess.run([str(PY),"-m","epv.reproduce"],cwd=ROOT,text=True,capture_output=True,env=env)
        self.assertEqual(p.returncode,0,p.stderr); self.assertEqual(json.loads(p.stdout)["status"],"PASS")

if __name__=="__main__": unittest.main()
