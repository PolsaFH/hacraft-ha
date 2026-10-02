"""Run with: python3 tests/test_summary.py"""
import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "summary", pathlib.Path(__file__).parent.parent / "custom_components" / "hacraft" / "summary.py")
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)

ids = ["light.a", "light.b", "sensor.t", "camera.door", "switch.x"]
out = summary.summarize_exposure({"expose_all_domains": ["light"], "exposed_entities": ["sensor.t", "gone.entity"]}, ids)
assert out["visible_to_mod_by_domain"] == {"light": 2, "sensor": 1}
assert out["visible_to_mod_total"] == 3
assert out["individually_picked"] == 2
assert out["expose_all_domains"] == ["light"]
# nothing configured -> nothing visible, and no entity ids leak into the summary
empty = summarize = summary.summarize_exposure({}, ids)
assert empty["visible_to_mod_total"] == 0
assert "light.a" not in str(out)
print("summary tests ok")
