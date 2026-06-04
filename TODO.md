
Some rough ideas for future work:

- [x] CLI tool
- [x] leverage streaming "iterencode" of json.JSONEncoder
- integration with different (non-stdlib) JSON libraries
- also support Python `repr`?
- improve documentation
- compatibility with Windows-style line endings?
- [x] project structure with src folder
- test compatibility with tab indentation, or even space+tab mixing
- smarter flushing: see test_fold_iter_flushing_nested
- [x] release on PyPI
- automate release procedure through github actions?
