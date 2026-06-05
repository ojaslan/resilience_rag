import pytest
import time
from langchain.schema import Document

from chaos.engine import ChaosEngine
from chaos.faults.latency import inject_latency
from chaos.faults.bad_data import corrupt_documents, NOISE_PHRASES
from chaos.faults.api_failure import maybe_raise_api_error, SimulatedAPIError


def test_chaos_engine_disabled_by_default():
    engine = ChaosEngine(enabled=False)
    called = []
    def fn(): called.append(1); return "ok"
    result = engine.inject(fn)
    assert result == "ok"
    assert len(engine.event_log) == 0


def test_chaos_engine_enable_disable():
    engine = ChaosEngine(enabled=False)
    engine.enable()
    assert engine.enabled
    engine.disable()
    assert not engine.enabled


def test_latency_inject():
    start = time.time()
    inject_latency({"min_delay": 0.1, "max_delay": 0.2, "probability": 1.0})
    elapsed = time.time() - start
    assert elapsed >= 0.1


def test_latency_zero_probability():
    start = time.time()
    inject_latency({"min_delay": 5.0, "max_delay": 10.0, "probability": 0.0})
    elapsed = time.time() - start
    assert elapsed < 0.5  # should not sleep


def test_bad_data_append():
    docs = [Document(page_content="clean content", metadata={})]
    corrupted = corrupt_documents(docs, {"corruption_rate": 1.0, "mode": "append"})
    assert any(phrase in corrupted[0].page_content for phrase in NOISE_PHRASES)
    assert "clean content" in corrupted[0].page_content


def test_bad_data_replace():
    docs = [Document(page_content="clean content", metadata={})]
    corrupted = corrupt_documents(docs, {"corruption_rate": 1.0, "mode": "replace"})
    assert "clean content" not in corrupted[0].page_content


def test_bad_data_empty():
    docs = [Document(page_content="clean content", metadata={})]
    corrupted = corrupt_documents(docs, {"corruption_rate": 1.0, "mode": "empty"})
    assert corrupted[0].page_content == ""


def test_api_failure_raises():
    with pytest.raises(SimulatedAPIError):
        maybe_raise_api_error({"probability": 1.0})


def test_api_failure_no_raise():
    # Should not raise with probability 0
    maybe_raise_api_error({"probability": 0.0})


def test_chaos_engine_logs_events():
    engine = ChaosEngine(enabled=True)
    engine.set_faults(["latency"])
    def fn(): return "result"
    try:
        engine.inject(fn)
    except Exception:
        pass
    assert len(engine.event_log) >= 1
    assert engine.event_log[0]["fault"] == "latency"
