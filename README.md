
# JSON Reflow

Python library and CLI tool to reflow JSON files and streams,
to allow a better compromise between

- compactness:
  try to fit short arrays and objects on a single line,
  within a given line length limit
- human readability:
  indented JSON for larger constructs otherwise.



## The problem

Standard JSON serialization tools typically only support two extremes:

- put everything on a single line:
  the most compact, but very poor for human readability

- spread out each and every array item and object property on its own line
  with appropriate indentation to visualize the structure.
  This is easier for humans to parse visually
  (which is why it is often referred to as "prettifying" or "beautifying"),
  but for larger documents, this easily becomes unwieldy, "too vertical"
  and very space-inefficient because of all the repeated indentation.

JSON Reflow allows to find a better compromise:
only serialize arrays or objects over multiple lines
if the single-line approach would exceed a given line length.
