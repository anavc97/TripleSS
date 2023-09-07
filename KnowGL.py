import re
from transformers import pipeline
import pickle
from core.keyword_search import KeywordSearch 
import json
from sentence_transformers import SentenceTransformer, util
import os

class TripleLog():
    def __init__(self, triple):
        self.triple = triple
        self.answers = []
        self.counter=0

class KnowGL:
    def __init__(self):
        self.properties = open('property.json', 'r')
        self.pipe = pipeline("text2text-generation", model="/home/ana/ibm/knowgl-large")
        self.ST_model = SentenceTransformer('all-MiniLM-L6-v2')
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/prop_emb.pickle", "rb") as f:
            self.prop_emb = pickle.load(f)
        self.properties = json.load(self.properties)

    def get_qid_from_name(self, name, filter=False):
        searcher = KeywordSearch()
        responds, _ = searcher.get(name, limit=3, mode="a", lang="en", expensive=0, info=1)
        #print(f"Entity: {str(name)}, QID:{responds}") #get only qid
        if filter:
            return [l[0] for l in responds if l[1]>0.5]
        return [l for l in responds]
    
    def choose_prop(self, prop):
        
        #Property reccomendation system
        emb1 = self.ST_model.encode(prop)
        cos_simil = {}
        pid_list = []

        for pid, prop2 in self.prop_emb.items():
            emb2 = prop2
            cos = util.cos_sim(emb1, emb2)
            if cos>0.4:
                cos_simil[self.properties[pid]] = cos
        
        c_simil = sorted(cos_simil.items(), key=lambda x:x[1], reverse=True)
        for c in c_simil[:3]:
            for key, value in self.properties.items():
                if value == c[0]:
                    pid_list.append(key)
          
        return [c[0] for c in c_simil[:3]], pid_list
    
    def get_triple(self, text):

        triple_txt = self.pipe(text)[0]["generated_text"]
        print(f"{triple_txt}-{text}")
        
        pattern = r'\[([^#]+)#([^#]+)#[^\]]+\]'
        pattern = r'\[\(([^\[\]]+)\)\|\s*([^|]+)\s*\|\(([^\[\]]+)\)\]'
        subject_labels = []
        relation_labels = []
        object_labels = []
        
        matches = re.findall(pattern, triple_txt)
        for match in matches:
            subject, relation, obj = match
            subject_label = subject.split('#')[0].strip()
            relation_label = relation.strip()
            object_label = obj.split('#')[0].strip()

            subject_labels.append(subject_label)
            relation_labels.append(relation_label)
            object_labels.append(object_label)
            
        print(subject_labels, relation_labels, object_labels)

        return subject_labels, relation_labels, object_labels
    
    def register_log(self, log, head_label, select_prop, tail_label, submit, logfile):

        if (head_label,select_prop, tail_label) not in [triple_log.triple for triple_log in log]:
            print("##########adding new triple: ", (head_label,select_prop,tail_label))
            triple_log = TripleLog((head_label,select_prop,tail_label))
            log.append(triple_log)

        for triple_log in log: 
            if triple_log.triple == (head_label,select_prop, tail_label):
                print("##########adding to triple: ", (head_label,select_prop,tail_label))
                #Triple already registered
                triple_log.counter +=1
        
        triple_log.answers.append(submit)

        with open(logfile, "wb") as a:
            pickle.dump(log, a)
        
