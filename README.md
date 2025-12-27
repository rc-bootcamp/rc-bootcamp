# RC bootcamp: developer README
**Note**: This README is for authors, developers, and anyone interested in creating or updating RC bootcamp or contributing to the project.
If you want to access RC bootcamp materials, see https://rc-bootcamp.github.io/.

## Introduction

**RC bootcamp** is a platform to create introductory materials for **reservoir computing (RC)**.
We use [Jupyter Notebooks](https://jupyter.org/) and [Python](https://www.python.org/) so newcomers to coding can learn RC from basics to advanced topics through hands-on exercises.
Key features of this platform are listed below.

1. **Multi-language support**:
Use language tags in markdown cells to put multiple languages into the same notebook.
When building, the `Makefile` extracts only the sections tagged for the chosen language.
Those pieces are then combined into per-language notebooks, that is, a single source notebook can produce versions for different languages.
English (`en`) and Japanese (`ja`) are supported now; you can add other languages by adding tags and translations and updating `LANGUAGES` in the `Makefile`.

2. **Automatic fill-in-the-blank exercise generation**:
Add special markers in code cells and the build will replace those parts with placeholders (`...`) to create exercises.
You can also generate solution versions automatically enabling authors to maintain both exercises and solutions in the same notebook.
This cuts down on work and makes updating materials easier.

3. **Answer checking and display**:
We provide a simple tester (`test_func`) that runs learners' code on prepared datasets to automatically verify correctness.
This goes beyond running example code and helps learners build coding skills and a deeper understanding of RC.
We also provide `show_solution`, which prints model answers so learners can check solutions when stuck.

4. **High extensibility**:
Each chapter is a standalone notebook, making it easy to add, remove, or rearrange chapters.
RC moves fast, and new topics pop up often, so this layout helps keep the content current.
After chapter 9, the material shifts toward more advanced research topics, and we may add more chapters later.

## Installation
Clone the repo and enter the project directory:
```bash
git clone https://github.com/rc-bootcamp/rc-bootcamp.git
cd rc-bootcamp
```

We use [`uv`](https://docs.astral.sh/uv/) and [`VSCode`](https://code.visualstudio.com/) for development.
Install `uv` and then sync project dependencies with:

```bash
uv sync --dev --extra gpu
```

Use `--extra gpu` only for notebooks that need a GPU (e.g., chapter 7, 11); otherwise omit it.
After syncing, install [Playwright](https://playwright.dev/) browsers with:

```bash
playwright install
```

which is required to convert some notebooks specified in `Makefile` to markdown (`.md`) and PDF during the build.
Activate the virtualenv and run make to test the build (the first line assumes bash/zsh; on Windows use `.venv\Scripts\activate` instead):

```bash
source .venv/bin/activate
make
```

Or run the build with `uv`:

```bash
uv run make
```

A successful build creates `product/rc-bootcamp_[LANG][MODE_SUFFIX]/` directories for each language and mode.
By default, the build creates four product folders:
- `product/rc-bootcamp_en`: English exercise version.
- `product/rc-bootcamp_en_sol`: English solution version.
- `product/rc-bootcamp_ja`: Japanese exercise version.
- `product/rc-bootcamp_ja_sol`: Japanese solution version.

## Editing notebooks
Below are guidelines for editing notebooks (`.ipynb` files).
All notebooks are under `src/`.

### Markdown cells
Use language tags such as `[en]: #` and `[ja]: #` to include multiple languages in the same markdown cell.
Use `[END]: #` to end language-specific sections for shared content (e.g., math or figures).
The example below shows a markdown cell with English and Japanese parts, plus shared math.

```markdown
[en]: #
Hello, this is an English sentence.

[ja]: #
こんにちは、これは日本語の文章です。

[END]: #
$$
a + b = c
$$

[en]: #
where $a$, $b$, and $c$ are variables.

[ja]: #
ここで$a$、$b$、$c$は変数です。
```

During build, the English version (`en`) will include only the `[en]: #` sections and the shared content, while the blocks for other languages are omitted.
In this case, the English version becomes:

```markdown
Hello, this is an English sentence.

$$
a + b = c
$$

where $a$, $b$, and $c$ are variables.
```

The Japanese version (`ja`) will be:
```markdown
こんにちは、これは日本語の文章です。

$$
a + b = c
$$

ここで$a$、$b$、$c$は変数です。
```

To add another language, append its tag and content in the same way.
The new language tag should be appended to `LANGUAGES` in `Makefile`.
Use language tags following [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes) (e.g., `es` for Spanish, `zh` for Chinese).


#### Images
Put images in `assets/` and link them from notebooks in `src/` using a relative path like `../assets/example_image.webp`.
The build embeds images as base64.
For example, write:

```markdown
![Example image](../assets/example_image.webp)
```

This will be embedded in the built notebook like:

```markdown
<img src="data:image/webp;base64,iVBORw0KGgoAAAAN..." alt="example_image.webp"/>
```

#### Other markers
You can use several other markers in markdown cells.

##### `[tips]: #` `[/tips]: #`:
Content wrapped with `tips` markers becomes a collapsible widget.

```markdown
[tips]: #
This is a tip.

[/tips]: #
```

It expands during build to:

```markdown
<details><summary>tips</summary>

This is a tip.

</details>
```

##### `[figc]: #` `[/figc]: #`:
Content wrapped with `figc` is treated as a figure caption.
```markdown
![An example figure](path/to/figure.png)

[figc]: #
This is a caption for the figure.

[/figc]: #
```
It expands during build to:
```markdown
![An example figure](path/to/figure.png)

<figcaption align="center">

This is a caption for the figure.

</figcaption>
```
You can combine `figc` with language tags, but you must end each language block with `[END]: #` so the closing `[/figc]: #` applies to all languages.
```markdown
[figc]: #

[en]: #
Fig. 1: An example caption.

[ja]: #
図1: キャプションの例。

[END]: #

[/tips]: #
```

### Code cells
Several markers and helper functions are provided to create fill-in-the-blank exercises and check answers.

#### Markers for creating fill-in-the-blank exercises
Put the following special markers in code cells and the build will replace those parts with `...`.

##### `# BEGIN` / `# END`:
Content between them is replaced by `...`.

Example:

```python
def solution(year: int):
    # BEGIN Check if the year is a leap year.
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return True
    else:
        return False
    # END
```

Build result:

```python
def solution(year: int):
    # TODO: Check if the year is a leap year.
    ...
```

##### `# BLANK`
It replaces the whole expression on the line with `...`.
Example:

```python
def solution(x):
    y = x ** 2
    print(y)  # BLANK Print the processed value
    return y
```

Build result:

```python
def solution(x):
    y = x ** 2
    ...  # TODO Print the processed value
    return y
```

##### `# RIGHT`
It replaces the right-hand side expression with `...`.

Example:

```python
def solution(a, b, c):
    """Multiply (a + 5), (b + 2) and 3 * c and return the result."""
    a = a + 5  # RIGHT Add 5 to a
    b += 2  # RIGHT Add 2 to b
    c *= 3  # RIGHT Multiply c by 3
    return a * b * c
```

Build result:

```python
def solution(a, b, c):
    """Multiply (a + 5), (b + 2) and 3 * c and return the result."""
    a = ...  # TODO Add 5 to a
    b += ...  # TODO Add 2 to b
    c *= ...  # TODO Multiply c by 3
    return a * b * c
```

##### `# RIGHT_B` / `# RIGHT_E`
It replaces right-hand side expressions inside the block with `...`.

Example:
```python
def solution(x, y, z, a=10, b=28, c=8.0 / 3.0):
    # RIGHT_B Implement the Lorenz system differential equations.
    x_dot = a * (y - x)  # NOTE: The comment is omitted.
    y_dot = x * (b - z) - y
    z_dot = x * y - c * z
    # RIGHT_E
    return x_dot, y_dot, z_dot
```

Build result:

```python
def solution(x, y, z, a=10, b=28, c=8.0 / 3.0):
    # TODO Implement the Lorenz system differential equations.
    x_dot = ...
    y_dot = ...
    z_dot = ...
    # end of TODO
    return x_dot, y_dot, z_dot
```

#### Checking answers and showing solutions
`test_func` and `show_solution` help test learner's code.
Example: load them from a chapter in `src`:

```python
from utils.tester import load_from_chapter_name

test_func, show_solution = load_from_chapter_name("SAMPLE_CHAPTER")
```

Put datasets and model answers under `src/data/SAMPLE_CHAPTER/`.
For a simple addition problem `sample_problem`, the problem cell can be:

```python
def solution(a, b):
    # BEGIN Implement addition of a and b.
    ans = a + b
    return ans
    # END

test_func(solution, "sample_problem")
show_solution("sample_problem", "solution")
```

The dataset and solution should be written in `src/data/SAMPLE_CHAPTER/sample_problem.py`.
Example:

```python
import random

from utils.tester import to_args


def solution(a, b):
    """
    This is the expected solution for addition of a and b.
    """
    ans = a + b
    return ans


def dataset():
    random.seed(1234)  # Change seed as needed
    yield to_args(3, 5)
    yield to_args(-1, 1)
    for _ in range(18):
        a = random.randint(-10000, 10000)
        b = random.randint(-10000, 10000)
        yield to_args(a, b)
```

`solution` is the expected answer and `dataset` yields test cases.
`test_func(solution, "sample_problem")` runs the learner's code on each case.
If all pass it prints `OK! (pass all cases)`.
If any fail it prints `Failed!` with input, expected, and actual outputs.
For multiple return values use `multiple_return=True`.
Pass a non-zero integer to `debug_mode` to see more details:
- `debug_mode=0` (default): only show pass/fail.
- `debug_mode=1`: show execution time per case.
- `debug_mode=2`: show inputs per case.
- `debug_mode=3`: show expected vs actual outputs.
- `debug_mode=-1`: show execution time only.
- `debug_mode=-2`: show execution time and inputs.
- `debug_mode=-3`: show time, inputs, and outputs.

`show_solution("sample_problem", "solution")` prints the `solution` function from `sample_problem.py`.
For the example it prints:

```
def solution(a, b):
    """
    This is the expected solution for addition of a and b.
    """
    ans = a + b
    return ans
```

To show another function, pass its name as the second argument.

#### Other markers
##### `[[BRANCH_NAME]]` / `[[PROJECT_NAME]]`
These markers are replaced during build with the `[LANG][MODE_SUFFIX]` (e.g., `en`, `ja_sol`) and project name (`rc-bootcamp`).
{ These markers are replaced during the build by the language+mode tag `[LANG][MODE_SUFFIX]` (e.g., `en`, `ja_sol`) and the project name (`rc-bootcamp`). }

## Build
The `Makefile` defines build behavior.
Below are main and helper targets.

### Main targets
`[LANG]` is a language code (e.g., `en` or `ja`) and `[MODE]` is `ex` (exercise, `[MODE_SUFFIX]` is `""`) or `sol` (solution, `[MODE_SUFFIX]` is `"_sol"`).

#### `make (make deploy)` / `make [LANG]` / `make [LANG]_[MODE]`
Running `make` defaults to `make deploy`.
The `make deploy` command builds the project using the steps below.

1. Run tests on all original source files (`.ipynb` and `.py`) in `src/`.
2. Create the `build/` directory.
3. Split notebooks in `src/` by language tags into `build/rc-bootcamp_[LANG][MODE_SUFFIX]/`.
4. Run syntax checks on all built `.ipynb` files in `build/rc-bootcamp_[LANG][MODE_SUFFIX]/`.
5. Convert selected notebooks (README.ipynb by default) to markdown (`.md`) and PDF (`.pdf`).
6. Copy built notebooks, converted files, and required root settings and libraries into `product/rc-bootcamp_[LANG][MODE_SUFFIX]/`.

`make deploy` builds all languages in `LANGUAGES` (default: `en ja`) and modes in `MODES` (default: `ex sol`), producing four output folders.
To build a single language or mode, run `make [LANG]` or `make [LANG]_[MODE]` (e.g., `make en` or `make ja_ex`).

You can include or exclude targets with `[LANG]_include` and `[LANG]_exclude` variables, which accept space-separated glob patterns for notebook filenames (without extensions).
For example, to build only chapters 1-5 and `README` in English exercise mode, run:

```bash
make en_ex en_include="01* 02* 03* 04* 05* README"
```

To build all chapters except chapters 7 and 11 in Japanese solution mode, run:

```bash
make ja_sol ja_exclude="07* 11*"
```

You can set these variables in the `Makefile` to avoid repeating them.
The `[LANG]_include` and `[LANG]_exclude` variables also work with `make dist` and `make test`, which is handy for building only part of the notebooks during translation.

#### `make dist` / `make [LANG]-dist` / `make [LANG]_[MODE]-dist`
`make dist` does the same as `make deploy` but creates a zip archive at `product/rc-bootcamp_[LANG][MODE_SUFFIX].zip` in stead of a folder in step 6.
For example, run `make en-dist` or `make ja_ex-dist` to archive a specific build.

#### `make mark` / `make [LANG]-mark` / `make [LANG]_[MODE]-mark`
`make mark` runs only steps 2, 3 and 5 of `make deploy` (Run test on source files, create the build dir, split notebooks by language tags, and convert notebooks to `.md`/`.pdf`).
It skips syntax checks and copying to `product/`.

#### `make test` / `make [LANG]-test` / `make [LANG]_[MODE]-test`
`make test` runs only steps 1, 2, 3, and 4 of `make deploy` (Create the build dir, split notebooks by language tags, and run syntax checks).
It does not convert notebooks to `.md`/`.pdf` or expand outputs under `product/`.
Tests use `tool/check_and_fix_notebook.py` and [`nbqa ruff`](https://github.com/nbQA-dev/nbQA); the lint rules come from `[tool.ruff.lint]` in `.pyproject.toml`.
Checks are as follows ( [VERSION] is the version in the `.python-version` file ).

- Metadata:
  - Whole notebook:
    - Check that `kernelspec` is set correctly.
      - `display_name` should be `rc-bootcamp ([VERSION])`.
      - `language` should be `python`.
      - `name` should be `python3`.
    - Check that `language_info` is set correctly.
      - `name` should be `python`.
      - `version` should be `[VERSION]`.
  - For each cell:
    - Ensure there are no unnecessary fields in cell metadata.

- For both code and markdown cells:
  - Ensure there are no empty cells.
  - Ensure there are no unnecessary leading blank lines (*).
  - Ensure there are no unnecessary trailing blank lines (*).
  - Ensure there are no trailing spaces at the end of lines (*).

- For markdown cells:
  - Header cells (`#, ##, ###, ####`, etc.) must not contain non-heading content (**)
    - This enhances readability and navigation.
  - Avoid two or more consecutive blank lines (*).
  - Do not leave a stray `[END]: #` marker at the end of a markdown cell.

- For code cells:
  - Ensure the execution count is null.
  - Ensure the cell output is cleared.
  - Ensure there are no ruff lint errors:
    - [`flake8-bugbear (B)`](https://docs.astral.sh/ruff/rules/#flake8-bugbear-b): Find likely bugs and design problems in your program.
    - [`pycodestyle (E, W)`](https://docs.astral.sh/ruff/rules/#pycodestyle-e-w): Check your Python code against some of the style conventions in PEP 8.
    - [`isort (I)`](https://docs.astral.sh/ruff/rules/#isort-i): Check that imports are sorted correctly.
    - [`Pyflakes (F)`](https://docs.astral.sh/ruff/rules/#pyflakes-f): Detect various errors in Python code.
    - [`numpy (NPY)`](https://docs.astral.sh/ruff/rules/#numpy-npy): Check for NumPy-specific coding issues.

These checks apply to notebooks under `src/` and `build/`.
Items marked with (*) are auto-fixed for notebooks in `build/` by `tool/check_and_fix_notebook.py` during `make test`, but those in `src/` must be fixed before building.
Items marked with (**) are not auto-fixed by `make beautify` and must be fixed manually.

The following rules are ignored during all tests:
- [`B018`](https://docs.astral.sh/ruff/rules/useless-expression/): Found useless expression. Either assign it to a variable or remove it.
- [`E402`](https://docs.astral.sh/ruff/rules/module-import-not-at-top-of-file/): Module level import not at top of cell.
- [`E501`](https://docs.astral.sh/ruff/rules/line-too-long/): Line too long ({width} > {limit})

In `ex` (exercise) mode, the following rules are additionally ignored:
- [`B007`](https://docs.astral.sh/ruff/rules/unused-loop-control-variable/): Checks for unused variables in loops (e.g., for and while statements).
- [`F401`](https://docs.astral.sh/ruff/rules/unused-import/): Checks for unused imports.
- [`F841`](https://docs.astral.sh/ruff/rules/unused-variable/): Checks for the presence of unused variables in function scopes.

### Helper targets
`Makefile` provides several helper targets.

#### `make archive`
Creates `product/rc-bootcamp_base.zip` using `git archive` of `HEAD`.

#### `make beautify`
Formats notebooks under `src/` with `tool/check_and_fix_notebook.py` and `nbqa ruff`, fixing most issues reported by `make test` except markdown heading problems.

#### `make clear` `make clean`
Removes build artifacts and intermediate files.
- `make clear`: deletes `product/`.
- `make clean`: deletes `product/` and `build/`.

#### `make help`
Lists available make targets.

```
Available make targets:
archive
beautify
clean
clear
deploy
dist
en
en-dist
en_ex
en_ex-dist
en_ex-test
en_sol
en_sol-dist
en_sol-test
en-test
help
ja
ja-dist
ja_ex
ja_ex-dist
ja_ex-test
ja_sol
ja_sol-dist
ja_sol-test
ja-test
test
test-src
```

## License
This project is licensed under the [MIT License](LICENSE.txt).

## Contributing
We welcome contributions from everyone.
To contribute to RC bootcamp, see [contributing guidelines](CONTRIBUTING.md).

## Contact
For questions or feedback contact `k-inoue[at]isi.imi.i.u-tokyo.ac.jp`.
