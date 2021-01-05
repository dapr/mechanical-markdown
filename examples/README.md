
# Quick Start

Once you have the package installed, if you want to try out some simple examples, navigate to the examples/ directory and have a look at start.md:

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

You can do a dry run to print out exactly what commands will be run using the '-d' flag.

```bash
mm.py -d start.md
```
You'll see output like the following:

```
Would run the following validation steps:
Step: First Step
	commands to run with 'bash -c':
		`echo "test"`
	Expected stdout:
		test
	Expected stderr:

```

Now you can run the steps and verify the output:

```bash
mm.py start.md
```

The script will parse the markdown, execute the annotated commands, and then print a report like this:

```
Running shell 'bash -c' with command: `echo "test"`
Step: First Step
	command: `echo "test"`
	return_code: 0
	Expected stdout:
		test
	Actual stdout:
		test
		
	Expected stderr:
	Actual stderr:
```

If anything unexpected happens, you will get report
of what went wrong, and mm.py will return non-zero.
