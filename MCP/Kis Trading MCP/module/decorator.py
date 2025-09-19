import threading


def singleton(cls):
    """
    클래스 형태를 유지하는 싱글톤 데코레이터.
    - 여러 번 호출해도 동일 인스턴스 반환
    - __init__은 최초 1회만 실행
    - 스레드-세이프
    """
    cls.__singleton_lock__ = getattr(cls, "__singleton_lock__", threading.Lock())
    cls.__singleton_instance__ = getattr(cls, "__singleton_instance__", None)

    orig_init = cls.__init__

    def __init__(self, *args, **kwargs):
        # 최초 1회만 실제 __init__ 수행
        if getattr(self, "__initialized__", False):
            return
        orig_init(self, *args, **kwargs)
        setattr(self, "__initialized__", True)

    def __new__(inner_cls, *args, **kwargs):
        if inner_cls.__singleton_instance__ is None:
            with inner_cls.__singleton_lock__:
                if inner_cls.__singleton_instance__ is None:
                    inner_cls.__singleton_instance__ = object.__new__(inner_cls)
        return inner_cls.__singleton_instance__

    cls.__init__ = __init__
    cls.__new__ = staticmethod(__new__)
    return cls
