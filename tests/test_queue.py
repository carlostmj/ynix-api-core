from app.queue.dispatcher import dispatch


def test_dispatch_sync_job():
    dispatch("example_job", {"name": "Carlos"})
