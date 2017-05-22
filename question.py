#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re, sys, nltk, string, codecs
from nltk import sent_tokenize
import spacy

nlp = spacy.load("en")

textFile = sys.argv[1]
total = int(sys.argv[2])

text = codecs.open(textFile, 'r', 'utf-8')
article = text.read()

art = re.split('\n+', article)
sents = []
num = 1

line = nlp(art[0])
to = list(line.noun_chunks)[0]
topic = to.text

#Tokenize into sentences
for x in art:
  sents = sents + sent_tokenize(x)
  
#Mark out special words
who = ["PERSON"]
what = ["NORP", "ORG", "PRODUCT", "WORK_OF_ART"]
whichLan = ["LANGUAGE"]
where = ["FACILITY", "GPE", "LOC", "EVENT"]
when = ["DATE", "TIME"]
howMuch = ["PERCENT", "MONEY"]
howMany = ["QUANTITY"]
which = ["ORDINAL", "CARDINAL"]
Nent = ['', 'ORDINAL', 'CARDINAL', 'QUANTITY', 'MONEY', 'PERCENT', 'TIME', 'DATE']
prop = ['he', 'she', 'it']

#main function
for y in sents:
  #give 'total' number of questions
  if num <= total:
    txt = nlp(y)
    root = [w for w in txt if w.head is w][0]
    Q = " "
    verb = " "
    sub = " "
    obi = " "
    su = []
    pun = [',', '.']
    entity = 0
    
    # look for sentence patterns with verbs
    if root.pos_ == "VERB" and root.text != "be":
      
      # find the questioning word
      if root.lemma_ == "be" or root.lemma_ == "have":
        Q = str(root).capitalize() + " "
      else:
        Q = "Did "
        verb = " " + str(root.lemma_) + " "
        
      # find the subject and verb, and turn the verb into basic form
      for x in txt.noun_chunks:
        if x.root.dep_ == "nsubj" and x.root.head == root:
          su = su + list(x)
        if x.root.dep_ == "nsubjpass" and x.root.head == root:
          su = su + list(x)
          Q = "Was "
          verb = " " + str(root) + " "
      for s in su:
        if s.ent_type_ not in Nent or s.lemma_ == "-PRON-":
          entity += 1
      if entity > 0:
        sus = []
        for s in su:
          if s.lemma_ == "-PRON-":
            top = topic
            if s.pos_ == "ADJ":
              top = topic + "'s"
            sus.append(top)
          else:
            sus.append(str(s))
      
        #join the sentence, take out extra part that is not in the root
        sub = " ". join(a for a in sus) 
        if list(root.rights) != []:
          obs = []
          for x in list(root.rights):
            ob = list(x.subtree)
            obs = obs + [str(a) for a in ob]
            if ob[0].pos_ != "PUNCT" and ob[-1].pos_ == "PUNCT":
              break
          if obs[-1] in pun:
            obs = obs[:-1]
            
          obj = " ".join(a for a in obs)

          sub = sub.decode("utf-8")
          verb = verb.decode("utf-8")
          obj = obj.decode("utf-8")
          yesStr = Q + sub + verb + obj + "?"
         
          #generate Wh- questions from yes/no questions
          whFind = nlp(yesStr)
          start = -1
          end = -1
          label = ""
          whWord = ""
          vb = ""
          for ent in whFind.noun_chunks:
            if whFind[ent.end].text != "'s":
              label = ent.root.ent_type_
              if ent.root.dep_ == "nsubj" and ent.root.head.lemma_ == root.lemma_:
                if label != "" and Q == "Did ":
                  start = ent.start
                  end = ent.end
                  start -= 1
                  end += 1
                  vb = root
                  break
                elif ent.root.text in prop:
                  start = ent.start
                  end = ent.end
                  whWord = "Who "
                  break
              else:
                start = -1
                end = -1
          if start >= 0:
            # find the Wh- word
            if label in who:
              whWord = "Who "
            elif label in what:
              whWord = "What "
            elif label in where:
              whWord = "Where "
            elif label in when:
              whWord = "When "
            elif label in howMuch:
              whWord = "How Much "
            elif label in howMany:
              whWord = "How Many "
            elif label in which:
              whWord = "Which "
            elif label in whichLan:
              whWord = "Which language "
            
            first = whFind[:start]
            if first[-1].pos_ == "DET" or first[-1].pos_ == "CONJ":
              first = first[:-1]

            last = whFind[end:]
            print(str(num) + ". " + whWord + str(first) + str(vb) + " " + str(last))
            num += 1
          # generate 'no' questions
          if num <= total:
            if num % 3 == 0:
              sub = u"the Spiderman"
            print(str(num) + ". " + Q + sub + verb + obj + "?")
            num += 1

    
    
    
    