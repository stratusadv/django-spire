import pickle


class CeleryNoResult:
    def __str__(self) -> str:
        return 'No Result'


def set_pickled_no_result() -> bytes:
    return pickle.dumps(CeleryNoResult())
