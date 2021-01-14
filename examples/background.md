# Sleeping, Timeouts, and Backgrounding

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

## Sleeping

Sometimes when running a series of steps automatically, they will run much faster than a human executing steps manually. If this leads to trouble for your procedures, you can insert a delay after running a command by using the ```sleep``` directive.

This first date command has a 5 second sleep:

<!-- STEP 
name: Step with a sleep
sleep: 5
expected_stdout_lines:
  - First step
-->

```bash
date
echo "First step"
```

<!-- END_STEP -->

You'll see at least a 5 second delay before this sleep gets executed:

<!-- STEP 
name: Delayed step
expected_stdout_lines:
  - Second step
-->

```bash
date
echo "Second step"
```

<!-- END_STEP -->

## Backgrounding

Conversely, if you want to run a step in the background without waiting to move on to the next step. This is great for starting services or daemons that you will clean up later on in the procedure. All backgrounded steps will be waited for at the end of execution so that stdout and stderr and the return code can all be checked. If a processes hasn't finished it will be timed out after 60s by default. See Timeout section below for more info.

In this first step, run a command that will take at least 5 seconds, but mm.py doesn't wait for it before executing the next step.

<!-- STEP 
name: Backgrounded step
background: true
expected_stdout_lines:
  - Background step
-->

```bash
sleep 5 && echo "Background step"
date
```

<!-- END_STEP -->

The next step will be executed right away, and the background step will be joined after all non-backgrounded steps have completed.

<!-- STEP 
name: Foreground step
expected_stdout_lines:
  - Foreground step
-->

```bash
echo "Foreground step"
date
```

<!-- END_STEP -->

## Timeouts

By default, all commands timeout after 60s. They will receive a SIGTERM, followed by a SIGKILL. Script that reach their timeout and are killed will cause validation to fail and mm.py will return non-zero. You can change the duration of the timeout for an individual step by setting ```timeout_seconds``` .

> **Note:** sleep time does not count towards timeout_seconds.

<!-- STEP 
name: Timeout step
timeout_seconds: 5
expected_stdout_lines:
  - Timeout step
-->

```bash
echo "Timeout step"
date
```

<!-- END_STEP -->

# Navigation

Back to [Working Directory](working_dir.md)
