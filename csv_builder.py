from core.db_wd import DBWikidata
from core.keyword_search import KeywordSearch
import en_core_web_sm, en_core_web_trf
import string
import random
import json
from vocabulary.vocabulary import Vocabulary as vb
from nlp import find_entities
from collections import Counter
from sentence_transformers import SentenceTransformer, util
import re
import pickle
import os

ID = "roger"

class TripleLog():
    def __init__(self, triple):
        self.triple = triple
        self.answers = []
        self.counter=0

class CSV():
    def __init__(self):
        self.nodes = []
        self.edges = []

logfile = f"{os.path.dirname(os.path.abspath(__file__))}/log_{ID}.pickle"
logfile_GT = f"{os.path.dirname(os.path.abspath(__file__))}/triples_GT.txt"

triple_list = []
csv = CSV()
MIN = 1


with open(logfile, "rb") as f:
    log = pickle.load(f)

#Clearing up info from logs
for lg in log:
    if lg.triple[0] == None or lg.triple[1][0] == None or lg.triple[2] == None or lg.counter < MIN:
        print("triple rejected: ", lg.triple)
        continue
    triple_list.append(lg.triple)

print("triple list: ", triple_list)

heads = [triple[0][2] for triple in triple_list]
tails = [triple[2][2] for triple in triple_list]
heads_qid = [triple[0][0] for triple in triple_list]
tails_qid = [triple[2][0] for triple in triple_list]
prop_ids = [triple[1][0] for triple in triple_list]

for head in heads:
    if head not in csv.nodes:
        csv.nodes.append(head)

for tail in tails:
    if tail not in csv.nodes:
        csv.nodes.append(tail)

for triple in triple_list:
    # Edge : (head_id, tail_id, prop_label)
    csv.edges.append((csv.nodes.index(triple[0][2]), csv.nodes.index(triple[2][2]), triple[1][1]))

print(csv.edges)
# Open the file in append mode
with open(f"nodes_{ID}.csv", "a") as file:
    # Write the sentence to the file
    file.write(f"Id,Label\n")
    for node in csv.nodes:
        file.write(f"{csv.nodes.index(node)},{node}\n")

with open(f"edges_{ID}.csv", "a") as file:
    # Write the sentence to the file
    file.write(f"Source,Target,Label\n")
    for edge in csv.edges:
        file.write(f"{edge[0]},{edge[1]},{edge[2]}\n")

with open(f"qids_{ID}.txt", "a") as file:
    # Write the sentence to the file
    for i in range(len(heads_qid)):
        file.write(f"{heads_qid[i]},{prop_ids[i]},{tails_qid[i]}\n")

with open(f"triples_{ID}.txt", "a") as file:
    # Write the sentence to the file
    for i in range(len(triple_list)):
        file.write(f"{triple_list[i][0][2]}-{triple_list[i][1][1]}-{triple_list[i][2][2]}\n")

