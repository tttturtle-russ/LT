import os
import subprocess

from openai import OpenAI
from pathlib import Path

base_prompt = """
# Role: Translator and Formatting Expert

## Profile
- author: MarkLee 
- version: 1.0
- language: 中英双语
- description: 你是一名翻译专家，擅长中英文的精准翻译。你将从 .rst 文件中接收到英文文本片段，并将其翻译成中文，同时保持原始格式不变。你的翻译精确，力求在结构、内容、写作风格和语气上与原文一致。翻译过程中，需严格遵守以下规则

## Skills
1. 中英双语翻译专家，能够精准翻译文本并保持一致性
2. 擅长处理技术文档，确保格式、代码块及特定词汇不被翻译
3. 擅长控制行长，保证中文翻译与英文长度相近，且每行字符不超过80个英文字符
4. 保持文本内容、格式和语气与原文完全一致

## Rules
1. 翻译时，每行字符数限制在 80 个英文字符内，一个中文字符相当于两个英文字符
2. 使每行长度尽量保持一致
3. 在翻译过程中保持与原文内容、风格、格式和语气的一致性
4. 不翻译代码块或特定词汇
5. 保证翻译的准确性，不对原始内容做出任何修改或遗漏
6. 中英文之间需要增加空格
7. 中文与数字之间需要增加空格
8. 全角标点与其他字符之间不加空格
9. 专有名词使用正确的大小写
10. 链接之间增加空格
11. 在译文的开头记得声明证书以及包含中文免责声明，如下:
.. SPDX-License-Identifier: GPL-2.0

.. include:: ../disclaimer-zh_CN.rst
12. 完整的代码字符串和完整的英文名词应当提前换行，防止被截断

## Workflows
1. 接收英文文本并分析其内容结构
2. 开始逐行翻译文本，确保每行字符数符合规则要求
3. 检查翻译后的文本是否保持格式和一致性，不修改代码块和特定词汇
4. 对比翻译后的文本与原文，确保内容和风格完全一致
5. 输出翻译后的中文文本，保留原文格式和代码

## Example:
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
            base_url="https://open.bigmodel.cn/api/paas/v4/",
            api_key="17d9adc522cdad2d425d70679fd4f4da.8XoYwLukFlVHTV7D"
        )
        self.__init_repo()
        os.chdir(self.path / target)
        self.output_dir = self.path / "../.." / target
        if not self.output_dir.exists():
            self.output_dir.mkdir(exist_ok=True, parents=True)

    @staticmethod
    def assistant_message(content):
        return {
            "role": "system",
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
        print(os.getcwd())
        for target in self.target:
            self.messages = [self.assistant_message(self.prompt)]
            original_text = open(target, "r").read()
            self.messages.append(self.user_message(original_text))
            resp = self.client.chat.completions.create(
                messages=self.messages,
                model="glm-4",
                top_p=0.7,
                temperature=0.9
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

    def test(self):
        completion = self.client.chat.completions.create(
        model="glm-4",  
        messages=[    
            {"role": "system", "content": "你是一个聪明且富有创造力的小说作家"},    
            {"role": "user", "content": "请你作为童话故事大王，写一篇短篇童话故事，故事的主题是要永远保持一颗善良的心，要能够激发儿童的学习兴趣和想象力，同时也能够帮助儿童更好地理解和接受故事中所蕴含的道理和价值观。"} 
        ],
        top_p=0.7,
        temperature=0.9
        )
        print(completion.choices[0].message)

def main():
    # from src.lt.translator import Translator
    from argparse import ArgumentParser

    argparse = ArgumentParser()
    argparse.add_argument("path")
    argparse.add_argument("target")
    argparse.add_argument("model")

    args = argparse.parse_args()

    path = args.path
    target = args.target
    model = args.model

    translator = Translator(path=path, target=target, model=model)
    translator.translate()
    # translator.translate()


if __name__ == "__main__":
    main() 