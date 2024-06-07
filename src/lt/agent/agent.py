import abc
import os

from openai import OpenAI
from pathlib import Path

base_prompt = """You are a translator and an expert in both Chinese and English. You will receive a text snippet from 
a .rst file. The file is also written in English. As a translation tool, you will solely return the same string in 
Chinese without losing or amending the original formatting. Your translations are accurate, aiming not to deviate 
from the original structure, content, writing style and tone. Along with the translation process, you must obey rules 
as follows: 
1. Your translation should restrict each line within 80 English characters, one Chinese character equals 
two English characters. 
2. Try your best to keep the same length for each line. 
3. Keep consistency with original text"""


class BaseAgent:
    def __init__(self, repo, target):
        self.prompt = base_prompt
        self.target = target
        self.client = OpenAI(
            base_url="http://localhost:8000/v1",
            api_key="NA"
        )
        self.repo = repo
        self.path = Path(f"/tmp/LT/{repo}")
        self.__init_repo()

    def __init_repo(self):
        if not self.path.exists():
            # if repo not exists, clone it to tmp
            os.system(f"git clone https://mirrors.hust.edu.cn/git/lwn.git {self.path}")
        self.path = self.path / "Documentation"
        if self.target not in self.path.iterdir():
            raise ValueError(f"No such file or directory: {self.target}")
        target = self.path / self.target
        if target.is_dir():
            self.target = list(target.glob("**/*.rst"))
        else:
            self.target = target

    @abc.abstractmethod
    def generate(self, input_text):
        raise NotImplementedError

    @abc.abstractmethod
    @property
    def name(self):
        raise NotImplementedError
