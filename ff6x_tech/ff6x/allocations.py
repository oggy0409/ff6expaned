"""Loader / validator for data/allocations.json (single source of truth)."""
import json
from .hirom import snes_to_pc, ROM_SIZE_VANILLA


class AllocationError(Exception):
    pass


class Allocations:
    def __init__(self, path):
        self.path = path
        with open(path) as f:
            self.raw = json.load(f)
        self.regions = []
        for r in self.raw["regions"]:
            r = dict(r)
            r["pc_start"] = snes_to_pc(int(r["snes_start"], 16))
            r["pc_end"] = snes_to_pc(int(r["snes_end"], 16))
            self.regions.append(r)
        self.claims = []
        for c in self.raw.get("vanilla_space_claims", []):
            c = dict(c)
            c["pc_start"] = snes_to_pc(int(c["snes_start"], 16))
            c["pc_end"] = snes_to_pc(int(c["snes_end"], 16))
            self.claims.append(c)
        self.tables = []
        for t in self.raw.get("vanilla_table_repacks", []):
            t = dict(t)
            t["pc_start"] = snes_to_pc(int(t["ptr_snes"], 16))
            t["pc_end"] = snes_to_pc(int(t["data_end_snes"], 16))
            self.tables.append(t)
        self.bits = {}
        for b in self.raw.get("event_bits", {}).get("allocated", []):
            if b["name"] in self.bits:
                raise AllocationError(f"duplicate event bit name {b['name']}")
            self.bits[b["name"]] = b
        nums = [(int(b["bit"], 16)) for b in self.bits.values()]
        if len(nums) != len(set(nums)):
            raise AllocationError("event bit allocated twice")
        self.validate()

    def validate(self):
        names = set()
        for r in self.regions:
            if r["name"] in names:
                raise AllocationError(f"duplicate region name {r['name']}")
            names.add(r["name"])
            if r["pc_start"] < ROM_SIZE_VANILLA or r["pc_end"] > 0x3FFFFF or r["pc_end"] < r["pc_start"]:
                raise AllocationError(f"region {r['name']} outside F0:0000-FF:FFFF or inverted")
        rs = self.regions
        for i in range(len(rs)):
            for j in range(i + 1, len(rs)):
                a, b = rs[i], rs[j]
                if set(a["targets"]) & set(b["targets"]) and not (a["pc_end"] < b["pc_start"] or b["pc_end"] < a["pc_start"]):
                    raise AllocationError(f"OVERLAPPING ALLOCATIONS: {a['name']} and {b['name']} "
                                          f"(shared targets {sorted(set(a['targets']) & set(b['targets']))})")
        for c in self.claims:
            if c["pc_end"] >= ROM_SIZE_VANILLA:
                raise AllocationError(f"vanilla claim {c['name']} is not in vanilla space")
        cs = self.claims
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                a, b = cs[i], cs[j]
                if set(a["targets"]) & set(b["targets"]) and not (a["pc_end"] < b["pc_start"] or b["pc_end"] < a["pc_start"]):
                    raise AllocationError(f"OVERLAPPING VANILLA CLAIMS: {a['name']} / {b['name']}")

    def active(self, target):
        return [r for r in self.regions if target in r["targets"]]

    def region(self, name, target):
        for r in self.regions:
            if r["name"] == name:
                if target not in r["targets"]:
                    raise AllocationError(f"region {name} not active for target {target}")
                if r["status"] in ("reserved", "blocked"):
                    raise AllocationError(f"region {name} is {r['status']}; writing requires manifest change")
                return r
        raise AllocationError(f"unknown region {name}")

    def covers(self, target, pc0, pc1):
        return any(r["pc_start"] <= pc0 and pc1 <= r["pc_end"] for r in self.active(target)
                   if r["status"] not in ("reserved", "blocked"))

    def table_covers(self, target, name, pc0, pc1):
        for t in self.tables:
            if t["name"] == name and target in t["targets"]:
                return t["pc_start"] == pc0 and pc1 == t["pc_end"]
        return False

    def table(self, name, target):
        for t in self.tables:
            if t["name"] == name and target in t["targets"]:
                return t
        raise AllocationError(f"table {name} not declared for {target}")

    def event_bits(self, target, audit):
        """name -> bit number for bits allocated to `target`, each verified
        FREE_CANDIDATE (vanilla-unreferenced, init 0) in the Rev 1 audit."""
        st = {r["bit"]: r for r in audit["rows"]}
        out = {}
        for name, b in self.bits.items():
            if target not in b["targets"]:
                continue
            row = st.get(b["bit"])
            if row is None or row["status"] != "FREE_CANDIDATE":
                raise AllocationError(f"bit {b['bit']} ({name}) is not FREE_CANDIDATE in the audit")
            kind = "EVENT" if b["kind"] == "event" else "NPC"
            if row["range"] != kind:
                raise AllocationError(f"bit {b['bit']} ({name}) kind/range mismatch")
            out[name] = int(b["bit"], 16)
        return out

    def retarget_ok(self, target, operand_snes, nbytes):
        """True if (operand_snes, nbytes) is the operand of a declared consumer instruction
        for this target (map v0.4 and/or monster v0.5 relocation lists)."""
        vr = self.raw.get("vanilla_operand_retargets")
        if not vr:
            return False
        if isinstance(vr, dict):
            vr = [vr]
        import os
        if not hasattr(self, "_retarget_sets"):
            self._retarget_sets = {}
        for src in vr:
            if target not in src["targets"]:
                continue
            key = src["source"]
            if key not in self._retarget_sets:
                d = json.load(open(os.path.join(os.path.dirname(self.path), os.path.basename(key))))
                ops = set()
                for t in d["tables"].values():
                    for c in t["consumers"]:
                        a = int(c["snes"], 16)
                        n = {"long": 3, "long_bank": 3, "imm_bank": 1, "imm_near": 2}.get(c.get("kind", "long"))
                        ops.add((a + 1, n))
                self._retarget_sets[key] = ops
            if (operand_snes, nbytes) in self._retarget_sets[key]:
                return True
        return False

    def vanilla_ref_bits(self, target):
        """name -> bit for vanilla bits a target may READ (never write)."""
        out = {}
        for b in self.raw.get("event_bits", {}).get("vanilla_read_only_refs", []):
            if target in b["targets"]:
                if b.get("access") != "read":
                    raise AllocationError(f"vanilla ref {b['name']} must be access=read")
                if b["name"] in self.bits:
                    raise AllocationError(f"vanilla ref {b['name']} collides with an allocated bit name")
                out[b["name"]] = int(b["bit"], 16)
        return out

    def vanilla_qa_write_bits(self, target):
        """TECH v0.9.2: name -> bit for vanilla bits a QA HARNESS package may WRITE (to emulate a later story state,
        e.g. 'the airship is available'); never available to production packages (checked by patches/map_v04.py)."""
        out = {}
        for b in self.raw.get("event_bits", {}).get("vanilla_qa_write_refs", []):
            if target in b["targets"]:
                if b.get("access") != "qa_write":
                    raise AllocationError(f"vanilla QA write ref {b['name']} must be access=qa_write")
                if b["name"] in self.bits:
                    raise AllocationError(f"vanilla QA write ref {b['name']} collides with an allocated bit name")
                out[b["name"]] = int(b["bit"], 16)
        return out

    def claim_covers(self, target, name, pc0, pc1):
        for c in self.claims:
            if c["name"] == name and target in c["targets"]:
                return c["pc_start"] <= pc0 and pc1 <= c["pc_end"]
        return False
