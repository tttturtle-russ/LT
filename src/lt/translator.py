import os
import subprocess

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
3. Keep consistency with original text.
4. Do NOT translate code block or specific word.
Here is an example:
Origin text:

===========
Hello World
===========

This is a hello world code in C language

.. ::code: c
    #include<stdio.h>
    
    int main() {
        printf("Hello World");
        return 0;
    }
    
Translation should looks like this:

==========
你好，世界
==========

这是一个用 C 语言编写的你好世界代码。

.. ::code: c
    #include<stdio.h>
    
    int main() {
        printf("Hello World");
        return 0;
    }
"""


class Translator:
    def __init__(self,
                 path,
                 target,
                 model):
        self.model = model
        self.path = Path(path)
        self.target = target
        self.prompt = base_prompt
        self.messages = [{"role": "system", "content": self.prompt}]
        self.client = OpenAI(
            base_url="http://localhost:8000/v1",
            api_key="NA"
        )
        self.__init_repo()
        os.chdir(self.path / target)
        self.output_dir = self.path / "translations/zh_CN" / target
        if not self.output_dir.exists():
            self.output_dir.mkdir(exist_ok=True, parents=True)

    @staticmethod
    def assistant_message(content):
        return {
            "role": "assistant",
            "content": content
        }

    @staticmethod
    def user_message(content):
        return {
            "role": "user",
            "content": content
        }

    def __init_repo(self):
        """
        __init_repo init the kernel repo and change self.path to target directory
        after called, self.target is a list of .rst file
        :return:
        """
        if not self.path.exists():
            # if repo not exists, clone it to /tmp/LT
            os.system(f"git clone https://mirrors.hust.edu.cn/git/lwn.git {self.path}")
        os.system(f"cd {self.path} && git checkout docs-next")
        self.path = self.path / "Documentation"
        self.target = self.path / self.target
        if self.target not in self.path.iterdir():
            raise ValueError(f"No such target: {self.target}")
        if self.target.is_dir():
            self.target = [target.name for target in (self.target.glob("**/*.rst"))]
        # os.system("cd lwn && make cleandocs && make htmldocs")

    def save(self, target, translation):
        with open(self.output_dir / target, "w+", encoding="utf-8") as f:
            f.write(translation)

    def translate(self):
        for target in self.target:
            self.messages = [self.assistant_message(self.prompt)]
            original_text = open(target, "r").read()
            self.messages.append(self.user_message(original_text))
            resp = self.client.chat.completions.create(
                messages=self.messages,
                model=self.model,
            )
            translation = resp.choices[0].message.content
            self.messages.append(self.assistant_message(translation))
            self.save(target, translation)

    @staticmethod
    def __check_error(target):
        # make htmldocs 2 >& 1
        p = subprocess.run("make htmldocs 2>&1", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if p.returncode != 0:
            raise RuntimeError(f"Error while compiling: {p.stderr}")
        if target in p.stdout:
            print("Error about translation format")
            return False
        return True
