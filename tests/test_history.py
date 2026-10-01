"""Run with: python3 tests/test_history.py"""
import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "history", pathlib.Path(__file__).parent.parent / "custom_components" / "hacraft" / "history.py")
history = importlib.util.module_from_spec(spec)
spec.loader.exec_module(history)

assert history.state_to_number("21.5") == 21.5
assert history.state_to_number(" -3 ") == -3.0
assert history.state_to_number("on") == 1.0
assert history.state_to_number("Closed") == 0.0
assert history.state_to_number("unavailable") is None
assert history.state_to_number("nan") is None
assert history.state_to_number("inf") is None
assert history.state_to_number(None) is None

# a value holds until it changes; slots before the first known value are None
pts = [(15.0, 1.0), (55.0, 5.0)]
assert history.downsample(pts, 0.0, 100.0, 10) == [None, 1.0, 1.0, 1.0, 1.0, 5.0, 5.0, 5.0, 5.0, 5.0]
assert history.downsample([], 0.0, 100.0, 4) == [None, None, None, None]
assert history.downsample([(0.0, 7.0)], 0.0, 100.0, 3) == [7.0, 7.0, 7.0]
assert history.downsample(pts, 100.0, 0.0, 4) == []
print("history tests ok")
