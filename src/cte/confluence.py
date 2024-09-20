import json
import re
from typing import Dict, List, Tuple
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, Tag
import pandas as pd


def stringify_task_body(body_node):
    s = ''
    try:
        for child in body_node.contents:
            if child.name == 'date':
                s += child.attrs['datetime']
            else:
                s += stringify_task_body(child)
    except AttributeError:
        return body_node.text
    return s


class ConfluenceInterface:
    def __init__(self, base_url: str, rest_url: str, token: str):
        self.base_url = base_url
        self.rest_url = rest_url
        self.token = token

    def make_request(self, endpoint: str):
        req = Request(
            f'{self.rest_url}{endpoint}',
            headers={
                'Authorization': f'Bearer {self.token}'
            }
        )
        with urlopen(req) as response:
            return json.load(response)

    def make_heading_link(self, page_data: Dict, heading_node: Tag | None) -> str:
        page_id = page_data['id']
        url = f'{self.base_url}pages/viewpage.action?pageId={page_id}'
        if heading_node is None:
            return url
        text = re.sub(r'[ _:-]', '', heading_node.text)
        title = re.sub(r'[ _:-]', '', page_data['title'])
        return url + f'#id-{title}-{text}'

    def get_task_frame(self, page_ids: List[str]) -> pd.DataFrame:
        task_data = {}
        user_cache = UserCache(self)
        for page_id in page_ids:
            data = self.make_request(f'content/{page_id}?expand=body.storage')
            html = f'<html xmlns:ac="http://example.com/ac" xmlns:ri="http://example.com/ri">{data["body"]["storage"]["value"]}</html>'

            task_list = self.parse_tasks_from_html(html, user_cache)
            for task_id, text, task_status, user_string, task_deadline, heading_node in task_list:
                link = self.make_heading_link(data, heading_node)
                task_data[task_id] = (text, task_status, user_string, task_deadline, link)

        sheet = pd.DataFrame(
            task_data.values(),
            columns=['Name', 'Status', 'User', 'Deadline', 'URL'],
            index=list(task_data.keys())
        )
        return sheet

    @staticmethod
    def parse_tasks_from_html(html: str, user_cache: 'UserCache') -> List[Tuple]:
        soup = BeautifulSoup(html, 'lxml')
        tasks = soup.find_all('ac:task')
        result_list = []
        for task in tasks:

            task_id_node = task.find('ac:task-id')
            task_id = int(task_id_node.text)

            task_status_node = task.find('ac:task-status')
            task_status = task_status_node.text == 'complete'

            task_body_node = task.find('ac:task-body')
            text = stringify_task_body(task_body_node).strip()

            task_time_node = task_body_node.find('time')
            task_deadline = None
            if task_time_node is not None:
                task_deadline = task_time_node.attrs['datetime']
            else:
                # we search for manual dates with a //<date> text
                deadline_text_match = re.search(r'//(\S+)', text)
                if deadline_text_match is not None:
                    task_deadline = deadline_text_match.group(1)
                    text = text.replace(deadline_text_match.group(0), '').strip()

            user_nodes = task_body_node.find_all('ri:user')
            user_keys = [user.attrs['ri:userkey'] for user in user_nodes]
            users = [user_cache.get(key) for key in user_keys]
            if len(users) == 0:
                # We attempt to find a non-confluence user mentioned with @name
                additional_users = re.findall(r'@\S+', text)
                for user in additional_users:
                    text = text.replace(user, '')
                text = text.strip()
                users.extend([user[1:] for user in additional_users])

            user_string = ','.join(users) if len(users) > 0 else None

            heading_node = task.find_previous(name=lambda x: x.name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'))

            result_list.append((task_id, text, task_status, user_string, task_deadline, heading_node))
        return result_list


class UserCache:
    def __init__(self, interface: ConfluenceInterface):
        self.cache = {}
        self.interface = interface

    def get(self, key: str) -> str:
        if key in self.cache:
            return self.cache[key]
        data = self.interface.make_request(f'user?key={key}')
        username = data['username']
        self.cache[key] = f'{username}@kit.edu'
        return self.cache[key]
