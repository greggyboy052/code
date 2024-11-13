import re
import os
from pydantic import BaseModel
from datasets import load_dataset
from langchain_openai import ChatOpenAI

from .base import Dataset
from .prompts.bigcodebench import DATA_SYNTH_PROMPT

class BigcodeBenchDataset(Dataset):
    name = "bigcodebench"

    def __init__(
        self,
    ):
        if os.getenv("OPENAI_API_KEY") is None:
            raise ValueError("OPENAI_API_KEY is not set")

        self.instruct_ds = load_dataset(
            "bigcode/self-oss-instruct-sc2-instructions", "instruct", streaming=True
        ).shuffle()
        self.instruct_iterset = iter(self.instruct_ds)

        self.gpt4 = ChatOpenAI(model="gpt-4o", temperature=0.7, max_tokens=64000)

        self.buffer = []

    def random(
        self,
        **kwargs,
    ):
        return self.get(
            **kwargs,
        )

    def get(
        self,
        **kwargs,
    ):
        if len(self.buffer) == 0:
            row = next(self.instruct_iterset)
            seed = row["seed"]
            response = self.gpt4.invoke(DATA_SYNTH_PROMPT + "\n" + seed).content

            # Extract all Python code blocks from the content
            code_blocks = re.findall(r"```python(.*?)```", response, re.DOTALL)

            # add all but last code block to buffer
            self.buffer.extend(code_blocks[:-1])

        content = self.buffer.pop(0)

        return {
            "title": "",
            "topic": "",
            "subtopic": "",
            "content": content,
            "internal_links": [],
            "external_links": [],
            "source": "GitHub",
            "tags": [],
            "extras": {},
        }

    def search(
        self,
    ):
        pass