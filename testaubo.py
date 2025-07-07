import libpyauboi5
import inspect

functions = [attr for attr in dir(libpyauboi5) if callable(getattr(libpyauboi5, attr))]

for func_name in functions:
    func = getattr(libpyauboi5, func_name)
    docstring = inspect.getdoc(func)
    print(f"Function: {func_name}")
    print(f"Docstring: {docstring}\n")