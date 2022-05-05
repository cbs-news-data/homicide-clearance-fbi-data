"""scans code and runs vulture and pylint"""

import subprocess

files = filter(
    lambda b: len(b) > 0,
    subprocess.check_output(
        [
            "find",
            "-name",
            "*.py",
            "-not",
            "-path",
            "./venv/*",
            "-not",
            "-path",
            "./scripts/*",
        ]
    )
    .decode("utf-8")
    .strip()
    .split("\n"),
)


for file in files:
    print(f"checking file '{file}'")
    subprocess.call(["vulture", file])
    subprocess.call(["pylint", file])
