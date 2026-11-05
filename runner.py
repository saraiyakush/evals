import yaml, subprocess, pathlib
import checker

pathlib.Path("results").mkdir(exist_ok=True)
article = open("article.txt").read()
DEFAULT_RUNS = 3

CONFIGS = ["with-skill", "without-skill"]   # A/B test directory names

def invoke_claude_in_isolation(prompt, config, file):
    # Replace local `claude` call with Anthropic or any other API call if using in agentic mode
    subprocess.run(["claude", "-p", prompt, "--output-format",
                    "stream-json", "--verbose"], cwd=config, stdout=file)

def run_assertions(case, config, run_result):
    for expected_key, expected_val in case["expect"].items():
        if config == "without-skill" and expected_key.startswith("skill_"):
            continue   # meaningless without the skill
        ok = checker.GRADERS[expected_key](run_result, expected_val)
        print(config, case["id"], run, expected_key, "PASS" if ok else "FAIL")

for case in yaml.safe_load(open("tldr-skill-tests.yaml")):
    prompt = case["prompt"].replace("{article}", article)
    for config in CONFIGS:
        for run in range(case.get("runs", DEFAULT_RUNS)):
            out_jsonl = f"results/{config}-{case['id']}-{run}.jsonl"
            with open(out_jsonl, "w") as f:
                invoke_claude_in_isolation(prompt, config, f)
            run_result = checker.extract_skills_and_response(out_jsonl)
            run_assertions(case, config, run_result)