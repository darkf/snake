**Snake** -- a (subset of) CPython bytecode interpreter in Python

This project leverages features from the CPython interpreter to write an interpreter for its bytecode, allowing the interpretation of arbitrary Python programs which can also use modules from CPython itself.

Currently it features:

  * int, str, etc.
  * lists, dictionaries and comprehensions
  * (non-closure) functions, loops, recursion
  
and a work-in-progress branch includes limited support for exception handling (try/catch), and
even more limited support for module imports.

This was written in one night on a whim, so don't dare expect it to be production quality.
Proceed at your own risk. :-)

License
=======

Licensed under the terms of the MIT license. Dive in.