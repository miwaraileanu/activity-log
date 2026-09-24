import threading
from agent.buffer import Buffer


def test_add_and_flush():
    b = Buffer()
    b.add({"x": 1})
    result = b.flush()
    assert result == [{"x": 1}]


def test_flush_empty():
    b = Buffer()
    assert b.flush() == []


def test_flush_clears():
    b = Buffer()
    b.add({"x": 1})
    b.flush()
    assert b.flush() == []


def test_thread_safety():
    b = Buffer()
    N = 100
    threads = [threading.Thread(target=lambda: [b.add({"i": i}) for i in range(N)]) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    result = b.flush()
    assert len(result) == N * 10
