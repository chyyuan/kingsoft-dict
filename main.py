# -*- coding:utf-8 -*-


import importlib
import json
import string
import sys
from urllib import request
from urllib.parse import quote

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

importlib.reload(sys)


class KingsoftDictExtension(Extension):

    def __init__(self):
        super(KingsoftDictExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def get_action_to_render(self, name, description, on_enter=None):
        item = ExtensionResultItem(name=name,
                                   description=description,
                                   icon='images/icon.png',
                                   on_enter=on_enter or DoNothingAction())
        return RenderResultListAction([item])

    def on_event(self, event, extension):
        query = event.get_argument()
        if query:
            url = 'http://dict-co.iciba.com/api/dictionary.php?type=json&key=F1D7870B690CBC2442A527DCB771E852&w=' + query
            s = quote(url, safe=string.printable)
            response = request.urlopen(s)
            rsp_data = response.read()
            obj = json.loads(rsp_data)

            parts = []
            if "parts" in obj["symbols"][0].keys():
                parts = obj["symbols"][0]["parts"]
                print(parts)

            items = []
            for part in parts:
                means = ''
                desc = ''
                if isinstance(part["means"][0], str):
                    means = '; '.join(part["means"])
                    desc = part["part"] + ' ' + means
                else:
                    for word in part["means"]:
                        means = means + word["word_mean"] + '; '
                    desc = means

                # 替换'<'、'>'字符，否则字符串无法正常显示
                desc = desc.replace('<', '[')
                desc = desc.replace('>', ']')

                items.append(
                    ExtensionResultItem(icon='images/icon.png', name=desc, on_enter=CopyToClipboardAction(desc)))

            if items:
                return RenderResultListAction(items)
            else:
                return self.get_action_to_render(name="Type in your query",
                                                 description="Example: word ")
        else:
            return self.get_action_to_render(name="Type in your query",
                                             description="Example: word ")


if __name__ == '__main__':
    KingsoftDictExtension().run()
