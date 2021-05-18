import time
import os
import json

csv_list = (
"data/query_activite.csv",
"data/query_poste.csv",
"data/query_oeuvre.csv",
"data/query_personne.csv",
"data/query_kingdom.csv",
"data/query_early_republic.csv",
"data/query_middle_republic.csv",
"data/query_late_republic.csv",
"data/query_high_empire.csv",
"data/query_low_empire.csv")

format_time = "%m/%d/%Y %I:%M:%S %p"
json_info = {}
info = []
for e in csv_list:
    metadata = os.stat(e)
    time_modif = time.strftime(format_time,time.localtime(metadata.st_mtime))
    size = (metadata.st_size)
    json_info ={
                "name": e,
                "time_modif": time_modif,
                "size":size
                }
    info.append(json_info)

with open("data/metadata.json", "w") as f:
    json.dump(list(info), f)
