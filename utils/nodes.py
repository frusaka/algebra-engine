def __getattr__(name: str):
    from datatypes import nodes

    return getattr(nodes, name)


__all__ = ["Var", "Const", "Complex", "Float", "Add", "Mul", "Pow"]
