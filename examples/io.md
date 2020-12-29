# I/O Validation

This is an example markdown file with an annotated test command.

To see a summary of what commands will be run:

```bash
mm.py -d io.md
```

To run this file and validate the expected output:

```bash
mm.py io.md
```

Be sure to checkout the raw version of this file to see the annotations.

This is an annotated command. When the ```mm.py``` utility is run, the following code block will be executed:

<!-- STEP
name: First Step
expected_stdout_lines:
  - "test"
-->

```bash
echo "test"
```

<!-- END_STEP -->

You can run multiple commands within the same block, and validate stderr as well.

> **Note:** The ```expected_stdout_lines``` and ```expected_stderr_lines``` directives ignore output that doesn't match an expected line. Validation will fail only if expected lines do not appear in stdout/stderr. You can have extra output and still pass validation.

<!-- STEP 
name: First Step
expected_stdout_lines:
  - "test"
  - "test2"
expected_stderr_lines:
  - "error"
-->

```bash
echo "test"
echo "another_output_line"
echo "test2"

echo "error" 1>&2
```

<!-- END_STEP -->

# Navigation

* Back to [README](README.md)
* On to [Environment Variables](env.md)

