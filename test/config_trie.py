import pprint
import json
import re

class Trie:
    def __init__(self):
        self.root = dict()

    def insert(self, line):
        cur = self.root
        for word in line.split():
            cur = cur.setdefault(word, {})
        cur['_end_'] = ''

    def search(self, line):
        cur = self.root
        for word in line:
            cur = cur.get(word)
            if not cur:
                return False
        return '_end_' in cur

    def traverse(self, node):
        word_list = []
        for key, value in node.items():
            if key != '_end_':
                for word in self.traverse(value):
                    # print("word is ", word)
                    words_to_add = key if word == '' else key + " " + word
                    word_list.append(words_to_add)
                    # print("word_list is ", word_list)
            else:
                word_list.append('')
        return word_list
        # if '_end_' in node:
        #     print("in _end_", line)
        #     word_list.append(line)
        # else:
        #     for k, v in node.items():
        #         line = line + " " + k
        #         self.traverse(v, line)
        #         print(line)
        # return word_list
    def get_whole_trie(self):
        return self.root

    def traverse_whole_trie(self):
        return self.traverse(self.root)

    def remove_from_list(self, del_list):
        for entities in del_list:
            keys = entities.split()
            cur = self.root
            for key in keys:
                cur = cur.get(key)
                # print(f'current {cur}, key is {key}')
                if not cur:
                    # print(f"{key} not found")
                    break
            try:
                # print(f'current {cur}, key is {key}')
                if cur:
                    cur.clear()
            except KeyError:
                print(f'Key not found')

# gold = make_config_into_trie("config-gold")
# this_config = make_config_into_trie("config-test")

# if key exists, delete it, or return None
# gold.root.pop('hostname', None)
# will have key error if non-exist key
# del gold.root['hostname']
# del gold.root['snmp-server']['enable']['traps']
# del gold.root['enable']['secret']
# gold.root['enable']['secret']['9']['[MASKED]'] = gold.root['license'].pop('udi')
# del gold.root['username']['enss']['privilege']['15']['secret']['9']


# if gold.get_whole_trie == this_config.get_whole_trie:
#     print("Matched")
# print("final ", t.traverse(t.root, ""))
# print("final ", t.traverse(t.root))
# whole_config = t.traverse(t.root)

# config_trie_to_file("bar", gold.traverse_whole_trie())
# config_trie_to_file("foo", this_config.traverse_whole_trie())


# t = Trie()
# t.insert("service tcp-keepalives-in")
# # t.insert("service tcp-keepalives-out")
# t.insert("service counters max age 10")
# t.insert("platform console serial")
# print(json.dumps(t.root, indent=4))
# print(t.search("service tcp-keepalives-out ok"))

# t1 = Trie()
# t1.insert("service tcp-keepalives-out")
# t1.insert("service counters max age 10")
# t1.insert("platform console serial")
# print(json.dumps(t1.root, indent=4))

# print(t1.root == t.root)
# print(t1.root["platform"] == t.root["platform"])
