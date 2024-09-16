from openai import OpenAI 
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
def assistant_message(content):
    return {
        "role": "system",
        "content": content
    }
def user_message(content):
    return {
        "role": "user",
        "content": content
    }
client = OpenAI(
    api_key="17d9adc522cdad2d425d70679fd4f4da.8XoYwLukFlVHTV7D",
    base_url="https://open.bigmodel.cn/api/paas/v4/"
) 
messages = [assistant_message(base_prompt)]
original_text = open("/home/lilanzhe/LT/lwn/Documentation/dev-tools/gpio-sloppy-logic-analyzer.rst", "r").read()
messages.append(user_message(original_text))
# print(messages)
completion = client.chat.completions.create(
    model="glm-4",  
    messages=messages,
    top_p=0.7,
    temperature=0.9
 ) 

with open("./gpio-sloppy-logic-analyzer.rst","w+",encoding="utf-8") as file:
    file.write(completion.choices[0].message.content) 
# print(completion.choices[0].message)