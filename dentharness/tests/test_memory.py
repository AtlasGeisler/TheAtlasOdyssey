import pytest

from dental_harness.memory import FileMemory


def test_remember_recall_forget(tmp_path):
    mem = FileMemory(tmp_path / "memory_store")
    mem.remember("doctors", "dr_geisler", {"report_window_hours": 24})
    assert mem.recall("doctors", "dr_geisler") == {"report_window_hours": 24}
    assert mem.keys("doctors") == ["dr_geisler"]
    assert mem.forget("doctors", "dr_geisler") is True
    assert mem.recall("doctors", "dr_geisler") is None


def test_recall_default(tmp_path):
    mem = FileMemory(tmp_path / "memory_store")
    assert mem.recall("ns", "missing", default="x") == "x"


def test_path_traversal_is_rejected(tmp_path):
    mem = FileMemory(tmp_path / "memory_store")
    with pytest.raises(ValueError):
        mem.remember("..", "..", "evil")
