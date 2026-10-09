import sys, os
sys.path.insert(0, 'tools')
import emu_harness
orig = emu_harness.H.shot
def shot(self, p):
    orig(self, p)
    if p.endswith("10a_chest_before.png"):
        open(os.environ["DUMP"], "wb").write(self.em.get_state())
        raise SystemExit("dumped")
emu_harness.H.shot = shot
import emu_celes_suite
sys.argv = ["x"] + sys.argv[1:]
emu_celes_suite.main()
