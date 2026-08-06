
# Changelog

## WIP 0.8.0

- Add `sort_keys` argument to `jsonreflow.dump()` and `jsonreflow.dumps()` ([#20](https://github.com/soxofaan/jsonreflow/issues/20))


## 0.7.1 - 2026-06-30

- `reflow_file()`: give `sink` argument default value `None` to make in-place reflowing easier
- Fix importability of `jsonreflow.reflow_file` ([#11](https://github.com/soxofaan/jsonreflow/issues/11), [#13](https://github.com/soxofaan/jsonreflow/issues/13))


## 0.7.0 - 2026-06-17

- Add `jsonreflow.reflow_file()` function to reflow a JSON file (given as path or file-like object)


## 0.6.0 - 2026-06-04

- Add `jsonreflow.dump(obj, fp)` ([#7](https://github.com/soxofaan/jsonreflow/issues/7))
- Support in-place file modification with CLI argument `--inplace` ([#2](https://github.com/soxofaan/jsonreflow/issues/2))


## 0.5.0 - 2026-05-30

- Expand README
- Add CLI argument `-i`/`--indent` to specify indentation level ([#3](https://github.com/soxofaan/jsonreflow/issues/3))


## 0.4.0 - 2026-05-30

- Rename project to `jsonreflow` ([#1](https://github.com/soxofaan/jsonfold/issues/1))


## 0.3.0 - 2026-03-09

- Switch to `src` layout


## 0.2.0 - 2026-02-27

- Add `jsonfold` command line tool.


## 0.1.0 - 2026-02-22

- Initial proof of concept implementation.
