from flask import Flask, render_template, request
from wikipedia_sections import main
import pickle, os, random
from KnowGL import KnowGL


class Dataset:
    def __init__(self, text,label):
        self.text = text
        self.label = label 

app = Flask(__name__)

dataset_file = f"{os.path.dirname(os.path.abspath(__file__))}/input.txt"
filename = f"{os.path.dirname(os.path.abspath(__file__))}/new_dataset_asia.pickle"
logfile = f"{os.path.dirname(os.path.abspath(__file__))}/log_victor.pickle"
triplefile = f"{os.path.dirname(os.path.abspath(__file__))}/triples_asia.pickle"

if os.path.isfile(logfile):
    print("##########Using log in: ", logfile)
    with open(logfile, "rb") as f:
        log = pickle.load(f)

else:
    print("##########No logfile found. Creating new one.")
    log = []

triples = {"head_labels":[], "tail_labels":[], "props":[]}
i = 0
kg = KnowGL()

def retrieve_all_triples(dataset_file):

    global triples

    f = open(dataset_file, "rb")

    dataset = []  # List to store the sentences

    try:
        with open(dataset_file, 'r') as file:
            
            for line in file:
                orig_query = line.strip()
                print("ORIGINAL QUERY: ", orig_query)
                heads, props, tails = kg.get_triple(orig_query)
                for a in heads:
                    triples["head_labels"].append(a)
                for b in props: 
                    triples["props"].append(b) 
                for c in tails:
                    triples["tail_labels"].append(c)

            return triples
    
    except FileNotFoundError:
        print(f"The file '{dataset_file}' does not exist.")
        return None



triples = retrieve_all_triples(dataset_file)

print("##########Triples: ", triples)

answer = None

def update_data():

    global kg, i, triples, head_label, tail_label, prop1, entity1_list, entity2_list, prop_list, prop_pid_list, head_label1, tail_label1

    head_label1 = triples["head_labels"][i]
    tail_label1 = triples["tail_labels"][i]
    prop1 = triples["props"][i]

    entity1_list = kg.get_qid_from_name(head_label1)
    entity1_list.append("None of the above")
    entity2_list = kg.get_qid_from_name(tail_label1)
    entity2_list.append("None of the above")
    prop_list, prop_pid_list = kg.choose_prop(prop1)
    prop_list.append("None of the above")
    print("lists: ", entity1_list, entity2_list)
update_data()

@app.route("/", methods=["POST", "GET"])  # this sets the route to this page
def home():

    if request.method == "POST":
        
        global kg, i, triples, head_label, tail_label, prop1, entity1_list, entity2_list, prop_list, prop_pid_list, head_label1, tail_label1

        print("##########answer:", request.form["entity1"], request.form["property"], request.form["entity2"], request.form["submit"])

        if request.form["submit"] == "Reject":
            kg.register_log(log, head_label1, [None,None], tail_label1, request.form["submit"], logfile)
            print("##########Reject")
        else:
            ent1_id = int(request.form["entity1"])
            prop_id = int(request.form["property"])  
            ent2_id = int(request.form["entity2"])
            if ent1_id == 3:
                head_label = "None"
            else:
                head_label = entity1_list[ent1_id]
            if prop_id == 3:
                prop = "None"
                prop_pid = "None"
            else:
                prop = prop_list[prop_id]
                prop_pid = prop_pid_list[prop_id]
            if ent2_id == 3:
                tail_label = "None"
            else:
                tail_label = entity2_list[ent2_id]
            kg.register_log(log, head_label, [prop_pid,prop], tail_label, request.form["submit"], logfile)
        
        i += 1
        
    if i < len(triples["head_labels"]): 
        update_data()
        return render_template("index.html", triple = (head_label1, prop1, tail_label1), entity1 = entity1_list, prop=prop_list, entity2=entity2_list)
    else: return render_template("end.html")

if __name__ == "__main__":
    
    # Start the loop in a separate thread
    #loop_thread = threading.Thread(target=update_data)
    #loop_thread.daemon = True  # Set as daemon thread to terminate when main thread exits
    #loop_thread.start()

    app.run()
