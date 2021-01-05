# Quick Start Example

This is an example markdown file with an annotated test command

<!-- STEP 
name: First Step
expected_stdout_lines:
  - "test"
-->

```bash
echo "test"
```

<!-- END_STEP -->

This unannotated command will not be run:
```bash
echo "A command that will not be run"
```
