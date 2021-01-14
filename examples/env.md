# Environment Variables

## Using this example
To see a summary of what commands will be run:

```bash
mm.py -d env.md
```

To run this file and validate the expected output:

```bash
mm.py
```

Be sure to checkout the raw version of this file to see the annotations.

## Setting environment variables for your commands

You can add environent variables by adding env to your step description yaml.
You can specify multiple environment variables as a dictionary of key value pairs.

<!-- STEP 
name: Step with environment variables
expected_stdout_lines:
  - env_value
  - env_value2
env:
  ENV_VARIABLE: env_value
  SECOND_ENV_VARIABLE: env_value2
-->

```bash
echo $ENV_VARIABLE
echo $SECOND_ENV_VARIABLE
```

<!-- END_STEP -->

<!-- STEP 
name: Override environment variables
expected_stdout_lines:
  - original
  - overridden
  - original
env:
  OVERRIDE_VARIABLE: original
-->

If your code block overwrites an environment variable, it will remain overridden to the end of the code block.

```bash
echo $OVERRIDE_VARIABLE
export OVERRIDE_VARIABLE=overridden
echo $OVERRIDE_VARIABLE
```

Context is not shared between code blocks (even in the same step). Each code block gets their own exectution environment.

```bash
echo $OVERRIDE_VARIABLE
```

<!-- END_STEP -->

# Navigation

* Back to [I/O Validation](io.md)
* On to [Working Directory](working_dir.md)
