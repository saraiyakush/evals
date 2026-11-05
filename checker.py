import json
from dataclasses import dataclass

from certifi import contents


@dataclass
class RunResult:
    loaded_skills: list[str]
    output_text: str

def extract_skills_and_response(path):
    lines = [json.loads(l) for l in open(path)]
    skills = [content["input"]["skill"] for line in lines if line.get("type") == "assistant"
              for content in line["message"]["content"]
              if content["type"] == "tool_use" and content["name"] == "Skill"]
    text = next(line["result"] for line in lines if line.get("type") == "result")
    return RunResult(skills, text)

rows = lambda text: text.strip().split("\n")

GRADERS = {
    "skill_loaded":         lambda run, expected: expected in run.loaded_skills,
    "skill_not_loaded":     lambda run, expected: expected not in run.loaded_skills,
    "bullet_count":         lambda run, expected: len(rows(run.output_text)) == expected,
    "max_words_per_bullet": lambda run, expected: all(len(row[2:].split()) <= expected for row in rows(run.output_text)),
    "first_line_is_bullet": lambda run, expected: rows(run.output_text)[0].startswith("- ") == expected,
}
