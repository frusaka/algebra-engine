def __getattr__(name: str):
    from datatypes import expr

    return getattr(expr, name)


__all__ = ["Var", "Const", "Complex", "Float", "Add", "Mul", "Pow"]
