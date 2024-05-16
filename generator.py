import json
import os
from pprint import pprint
import random
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-lang',
    type=str,
    help="add a dataset",
    required=True,
    choices=["it", "es"])

args = parser.parse_args()

templates = {}
htmls = {}
json_templates_path = os.path.join(args.lang, "json_templates")
html_templates_path = os.path.join(args.lang, "html_templates")
for file in os.listdir(json_templates_path):
    with open(os.path.join(json_templates_path, file)) as f:
        name = file.split(".")[0]
        templates[name] = json.loads(f.read()) 

for file in os.listdir(html_templates_path):
    with open(os.path.join(html_templates_path, file)) as f:
        name = file.split(".")[0]
        htmls[name] = f.read()
        
symphony = json.load(open(os.path.join(args.lang, "data", "symphony.json"), "r"))
amt_words = json.load(open(os.path.join(args.lang, "data", "amt_words.json"), "r"))
video_ids = json.load(open(os.path.join(args.lang, "data", "video_ids.json"), "r"))

output = []

parts = ["Parte 1:", "Parte 2: ", ]

id_step = 0
relaxation_video = ['VideoRelaxation.mp4', 'VideoEditado.mp4']
id_r = 0

for page in symphony['pages']:
    tmp = {k:v for k,v in templates['guidelines'].items()}
    tmp['id'] = len(output)
    tmp['html'] = htmls[page]
    output.append(tmp)
    if 'panas' in page:
        tmp = {k:v for k, v in templates['panas'].items()}
        tmp['id'] = len(output)
        tmp['guidelines'] = htmls['panas_reminder']
        output.append(tmp)
    elif "video" in page:
        for x in range(symphony['videos_to_annotate']):
            video = {k:v for k, v in templates['video_embedding'].items()}
            valence = {k:v for k, v in templates['valence'].items()}
            arousal = {k:v for k, v in templates['arousal'].items()}
            video['id'] = len(output)
            video['vid_name'] = video_ids[x]
            output.append(video)
            valence['id'] = len(output)
            valence['video_id'] = video_ids[x]
            valence['text'] = htmls['video_annotation_valence']
            output.append(valence)
            arousal['id'] = len(output)
            arousal['video_id'] = video_ids[x]
            arousal['text'] = htmls['video_annotation_arousal']
            output.append(arousal)
    elif "relaxation_phase_main" in page:
        video = {k:v for k, v in templates['video_embedding'].items()}
        video['id'] = len(output)
        video['vid_name'] = relaxation_video[id_r]
        output.append(video)
        id_r += 1
    elif "distraction" in page:
        tmp = {k: v for k,v in templates['distraction_task'].items()}
        tmp['id'] = len(output)
        # tmp['guidelines'] = htmls['distraction_task']
        output.append(tmp)
    elif "narrative" in page:
        tmp_amt_words = {"positve":  [el for el in amt_words['positive']], 
                            "negative": [el for el in amt_words['negative']]}
        # streak_of_words = []
        for x in range(symphony['amt_narratives']):
            # Word selection 
            # if x < len(tmp_amt_words.keys()):
            #     key = list(tmp_amt_words.keys())[x]
            # else:
            #     rand_key = random.choice(list(tmp_amt_words.keys()))
            
            key = list(tmp_amt_words.keys())[x%len(tmp_amt_words.keys())]    
            
            elem = random.choice(tmp_amt_words[key])
            tmp_amt_words[key].remove(elem)
            # streak_of_words.append(elem)
            # Page generation
            tmp_narrative = {k:v for k,v in templates['narrative'].items()}
            tmp_narrative['id'] = len(output)
            tmp_narrative['keyword'] = elem
            tmp_narrative['guidelines'] = htmls['narrative_amt'].replace("[TMP]", elem)
            output.append(tmp_narrative)
            # Simple checks
            if len(tmp_amt_words[key]) == 0:
                del tmp_amt_words[key]
            if len(tmp_amt_words) == 0:
                print("You run out of AMT words!")
                os._exit()
        
        for x in range(symphony['usom_narratives']):
            tmp_narrative = {k:v for k,v in templates['narrative'].items()}
            tmp_narrative['id'] = len(output)
            content = htmls['narrative_usom']
    
            if x % 2 ==0:
                content = content.replace("[HTML]", htmls['question_positive_usom'] )
                tmp_narrative['keyword'] =  htmls['question_positive_usom']
            else:
                content = content.replace("[HTML]", htmls['question_negative_usom'] )
                tmp_narrative['keyword'] =  htmls['question_negative_usom']
            tmp_narrative['guidelines'] = content
            output.append(tmp_narrative)

tmp = {k:v for k,v in templates['finale'].items()}     
tmp['id'] = len(output)
tmp['text'] = htmls['finale']
output.append(tmp)        


with open("test_pipeline.json", "w") as f:
    f.write(json.dumps(output, indent=4))   