# Skill Evals: A/B Testing a Claude Code Skill

> **Educational project.** This repository shows, in about 80 lines of Python and YAML, how to write automated evaluations for a [Claude Code skill](https://docs.claude.com/en/docs/claude-code/skills). It is a learning aid, not a production test harness.

The project tests a small skill called `tldr`. It checks two things:

1. **Triggering.** Does Claude load the skill when it should, and leave it alone when it shouldn't?
2. **Behavior.** When the skill is loaded, does the output follow the skill's rules?

Each test runs against two setups, one with the skill installed and one without, so you can compare the results side by side (an A/B test).

## How it works

```
tldr-skill-tests.yaml ──► runner.py ──► claude -p (headless) ──► results/*.jsonl
                                                                      │
                               PASS / FAIL  ◄── checker.py graders ◄──┘
```

Each case runs several times (3 by default) because model output is non-deterministic. A single pass tells you little; a pass rate across runs tells you more.

## Project structure

| Path | Purpose |
|---|---|
| `runner.py` | Runs the test cases against each setup and prints results. |
| `checker.py` | Parses Claude's stream-json output and defines the graders. |
| `tldr-skill-tests.yaml` | Test cases: prompt, number of runs, expected outcomes. |
| `article.txt` | Sample text used as input for the summary prompts. |
| `with-skill/.claude/skills/tldr/SKILL.md` | The skill under test. |
| `without-skill/` | Control setup with no skill installed. |
| `results/` | Raw `.jsonl` logs from each run. Created automatically. |

## The skill under test

`tldr` tells Claude to summarize pasted text as exactly 3 bullets, each 15 words or fewer, with no intro or closing line. The `description` field in the skill's frontmatter is what Claude reads to decide whether to load the skill, so the trigger tests mostly test how well that one sentence is written.

## Test cases

| ID | Prompt | Checks |
|---|---|---|
| `trigger-paraphrase` | "What's the gist of this? {article}" | Skill loads even though the prompt never says "summarize". |
| `trigger-negative` | "Write a poem about autumn" | Skill does **not** load for an unrelated task. |
| `behavior-format` | "Summarize: {article}" | Skill loads, and the output is 3 bullets of 15 words or fewer, starting with a bullet. |

## Graders

Defined in `checker.py` as a `GRADERS` dictionary. Each grader takes a run result and an expected value and returns `True` or `False`.

| Grader | Passes when |
|---|---|
| `skill_loaded` | The named skill appears in Claude's `Skill` tool calls. |
| `skill_not_loaded` | The named skill does not appear. |
| `bullet_count` | The response has exactly N lines. |
| `max_words_per_bullet` | Every line (after the 2-character `- ` prefix) has N words or fewer. |
| `first_line_is_bullet` | The first line starts with `- `. |

Graders whose names start with `skill_` are skipped for the `without-skill` setup, since the skill can't load there.

## Getting started

### Prerequisites

- Python 3.10 or later
- [Claude Code](https://docs.claude.com/en/docs/claude-code) installed, signed in, and on your `PATH` as `claude`
- If Needed: Python packages `pyyaml` and `certifi`

### Setup and run

```bash
python3 -m venv .venv
source .venv/bin/activate

# Optional, if below run fails
pip install pyyaml certifi

python runner.py
```

> :warning: Each run calls the model, so a full pass makes 18 Claude calls (3 cases × 2 setups × 3 runs) and uses your Claude usage or API credits.

### Example output

```
with-skill trigger-paraphrase 0 skill_loaded PASS
with-skill behavior-format 2 bullet_count FAIL
without-skill behavior-format 0 bullet_count FAIL
```

When a check fails, open the matching file in `results/` to see exactly what Claude did and said.

## Extending the project

- **Add a test case:** Append an entry to `tldr-skill-tests.yaml` with an `id`, a `prompt`, an optional `runs`, and an `expect` map that uses existing grader names.
- **Add a grader:** Add a `name: lambda run, expected: ...` entry to `GRADERS` in `checker.py`, then use `name` in a test's `expect` map.
- **Test a different skill:** Put its `SKILL.md` under `with-skill/.claude/skills/<name>/` and write test cases for it.
- **Use the API instead of the CLI:** Replace `invoke_claude_in_isolation` in `runner.py` with a call to the Anthropic API or another provider, as the comment there suggests.
- **Add a pass-rate summary and/or non-zero exit code:** A pass rate will determine if the skill passes each time beyond a threshold.

## Known limitations

These are simplifications kept on purpose to make the code short and easy to read:

- Results are printed only. There is no pass-rate summary or non-zero exit code on failure.
- The format graders treat every line as a bullet, so a blank line or a heading counts as a failed bullet.
- `run_assertions` reads the loop variable `run` as a global rather than taking it as a parameter.
