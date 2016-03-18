# -*- coding: utf-8 -*-

import re
import requests

from jinja2 import Environment, FileSystemLoader

PROJECT = "Mathe für Nicht-Freaks"
SITEMAP = PROJECT + ": Sitemap"
WIKI_DOMAIN = "de.wikibooks.org"

def get_wiki_page(domain, title):
    url = "https://" + domain + "/w/index.php"
    params = {
        "title": title,
        "action": "raw"
    }

    return requests.get(url, params = params).text

def read_nodes(sitemap_text):
    for line in sitemap_text.splitlines():
        if line.startswith(("=", "*")):
            node_type = line[0]
            node_level = len(line) - len(line.lstrip(node_type))

            if node_type == "=":
                line = line.strip(node_type)
            else:
                line = line.lstrip(node_type)

            line = line.strip()
            line = re.sub("\s+{{Symbol\|\d+%}}", "", line)

            node_name = line
            node_link = None

            if line.startswith("[[") and line.endswith("]]"):
                line = line.lstrip("[").rstrip("]")
                
                i = line.index("|")

                node_link = line[:i]
                node_name = line[i+1:] 

            yield Node(node_link, node_name,
                       0 if node_type == "=" else 1, node_level)

class Node(object):
    def __init__(self, node_link, node_name,
            node_type=-1, node_level=-1):
        self._type = node_type
        self._level = node_level
        self.link = node_link
        self.name = node_name
        self.children = []

    def is_over(self, other_node):
        if self._type != other_node._type:
            return self._type < other_node._type
        else:
            return self._level < other_node._level

    def add_node(self, other_node):
        if len(self.children) > 0:
            last_child = self.children[-1]
        else:
            last_child = None

        if (last_child == None or
                (self.is_over(other_node) and not
                last_child.is_over(other_node))):
            self.children.append(other_node)
        else:
            last_child.add_node(other_node)

    def is_article(self):
        return len(self.children) == 0 and self.link

    def print_tree(self, level=0):
        print("  " * level + self.name)

        for child in self.children:
            child.print_tree(level+1)

def parse_sitemap(sitemap_text):
    result = Node(PROJECT, PROJECT)

    for node in read_nodes(sitemap_text):
        result.add_node(node)

    return result

if __name__ == "__main__":
    sitemap_text = get_wiki_page(WIKI_DOMAIN, SITEMAP)
    sitemap = parse_sitemap(sitemap_text)

    sitemap.children = [ x for x in sitemap.children if x.name != "Informationen zum Projekt" and x.name != "Buchanfänge" ]

    env = Environment(loader = FileSystemLoader("."))
    template = env.get_template("sitemap.template")
    
    with open("sitemap.xml", "w") as fh:
        fh.write(template.render(sitemap = sitemap))
