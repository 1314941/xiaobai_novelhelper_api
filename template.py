import os
import json


path="template/"

user="/user.txt"
assistant="/ai.txt"
prompt="/prompt.txt"


# 读取JSON文件
class RoleData:
    def __init__(self):
        with open('role.json', 'r', encoding='utf-8') as file:
            self.data = json.load(file)
        self.data=self.data['system']
        
        self.init()


    def init(self):
        add_prompt(self.data)
        add_template(self.data)


    def get_role(self,role_name):
        for item in self.data:
            if item['role'] == role_name:
                return item
        return None




def add_template(data):
    for item in data:
        # if item['role'] == "章节提取器":
            #一个多行字符串，使用了三引号（"""）来表示，这样可以包含换行符。
            new_path=path+f"{item['id']}"+user
            if not os.path.exists(new_path):
                with open(new_path, 'w', encoding='utf-8') as file:
                    file.write("")
            with open(new_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                
            # 如果txt文件内容为空，则使用默认值
            if not template_content:
                with open(new_path, 'a', encoding='utf-8') as file:
                    file.write(item['template']['user'])
                    template_content = item['template']['user']
            item['template']['user'] = template_content

            new_path=path+f"{item['id']}"+assistant
            if not os.path.exists(new_path):
                with open(new_path, 'w', encoding='utf-8') as file:
                    file.write("")
            with open(path+f"{item['id']}"+assistant, 'r', encoding='utf-8') as file:
                template_content = file.read()
            if not template_content:
                with open(new_path, 'a', encoding='utf-8') as file:
                    file.write(item['template']['assistant'])
                    template_content = item['template']['assistant']
            item['template']['assistant'] = template_content


def add_prompt(data):
    for item in data:
        new_path=path+f"{item['id']}"+prompt
        if not os.path.exists(new_path):
            with open(new_path, 'w', encoding='utf-8') as file:
                file.write("")
        with open(new_path, 'r', encoding='utf-8') as file:
            template_content = file.read()
        # 如果txt文件内容为空，则使用默认值
        if not template_content:
            with open(new_path, 'a', encoding='utf-8') as file:
                file.write(item['description'])
        else:
            item['description'] = template_content
