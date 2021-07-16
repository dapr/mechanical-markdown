# Tagging

## Using This Guide
This is an example markdown file with an annotated test command.

To see a summary of what commands will be run:

```bash
mm.py -d tagging.md
```

To run this file and validate the expected output:

```bash
mm.py tagging.md
```

Be sure to checkout the raw version of this file to see the annotations.

## Tagging steps

Sometimes your documentation may contain steps that are only meant to be run on a particular platform, or in a particular circumstance. You can use the `tags` directive to specify a list of tags with each step.

<!-- STEP
name: Linux Step
expected_stdout_lines:
  - Linux
tags:
  - linux
-->

This step is tagged `linux`. If you run `mm.py -t linux`, this step will be executed.

```bash
echo "Linux"
```

<!-- END_STEP -->

This step is tagged `windows`. If you run `mm.py -t windows`, this step will be executed.

<!-- STEP
name: Windows Step
expected_stdout_lines:
  - Windows
tags:
  - windows
-->

```bash
cmd.exe /C "echo Windows"
```

<!-- END_STEP -->

This step is tagged with both `windows` and `linux`. If you run `mm.py -t windows` or `mm.py -t linux`, this step will be executed.

<!-- STEP
name: Windows Step
expected_stdout_lines:
  - Windows and Linux
tags:
  - windows
  - linux
-->

```bash
echo Windows and Linux
```

<!-- END_STEP -->

**Note:** If you run `mm.py` without any tags, all steps are run, tagged or not.

# Navigation

* Back to [Sleeping, Timeouts, and Backgrounding](background.md)


