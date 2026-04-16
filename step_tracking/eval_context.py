from functools import wraps

from .step import Step


_steps: dict = {}
_verbose: bool = True
_curr_hist: list = None


def set_verbosity(value: bool) -> None:
    global _verbose
    _verbose = value


def verbose() -> bool:
    return _verbose


def register(step: Step) -> None:
    if not _verbose:
        return
    _curr_hist.append(step)


def tracked(label: str):
    def tracked_func(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            history = [_steps.get(id(n), None) for n in args]
            wrapper.steps = history
            result = func(*args, **kwargs)
            del wrapper.steps

            if (
                _verbose
                and any(history)
                or wrapper._is_simplified
                and wrapper._is_simplified(result, args)
            ):
                args_ = ", ".join(
                    history[idx].before if history[idx] else str(args[idx])
                    for idx in range(len(args))
                ).join("()")
                step = Step(
                    label,
                    f"{func.__name__}{args_}",
                    f"{func.__name__}{args}",
                    result,
                    [i for i in history if i is not None],
                )
                _steps[id(result)] = step
            return result

        def simplify_rule(fn):
            wrapper._is_simplified = fn
            return fn

        wrapper._is_simplified = None
        wrapper.simplify_rule = simplify_rule
        return wrapper

    return tracked_func


def explain(expr):
    return _steps.get(id(expr), None)


__all__ = ["verbosity", "set_verbosity", "tracked", "explain", "register"]
