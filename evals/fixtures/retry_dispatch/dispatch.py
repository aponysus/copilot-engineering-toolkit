"""Synthetic in-memory dispatch with a deterministic transport failure."""


class Queue:
    def __init__(self) -> None:
        self.jobs: list[str] = []
        self.lose_next_response = True

    def submit(self, job: str) -> int:
        self.jobs.append(job)
        if self.lose_next_response:
            self.lose_next_response = False
            raise TimeoutError("response lost")
        return len(self.jobs)


def dispatch(queue: Queue, job: str) -> int:
    for attempt in range(2):
        try:
            return queue.submit(job)
        except TimeoutError:
            if attempt == 1:
                raise
    raise AssertionError("unreachable")
