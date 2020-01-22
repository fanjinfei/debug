import spacy
import neuralcoref

nlp = spacy.load('en_core_web_sm')
neuralcoref.add_to_pipe(nlp)
#doc1 = nlp('My sister has a dog. She loves him.')
doc1 = nlp('My sister has a dog. She loves her.')
print(doc1._.coref_clusters)

doc2 = nlp('Angela lives in Boston. She is quite happy in that city.')
for ent in doc2.ents:
    print(ent._.coref_cluster)

'''
git clone https://github.com/huggingface/neuralcoref.git
cd neuralcoref
pip install -r requirements.txt
pip install -e .
'''