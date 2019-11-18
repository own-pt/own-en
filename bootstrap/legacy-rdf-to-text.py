#!/bin/python3

# This script is very ad hoc and has lots of hardcoded stuff; this is
# by design, since it is only meant to be run once as bootstrap for
# the text files. run
## python <this-file>.py --help
# for options

import rdflib as r
from rdflib import Graph, Namespace
from rdflib.term import Literal


WN30 = Namespace("https://w3id.org/own-pt/wn30/schema/")
WN30EN = Namespace("https://w3id.org/own-pt/wn30-en/instances/")
WN30PT = Namespace("https://w3id.org/own-pt/wn30-pt/instances/") # not used (yet)

###
## fix some glosses
WN_GLOSS = WN30["gloss"]
WN_DEFINITION = WN30["definition"]
WN_EXAMPLE = WN30["example"]

def fix_glosses(graph):
    def split_gloss(gloss):
        def remove_quotes(example):
            example.strip()
            if example[-1] == "\"" and "\"" not in example[:-1]:
                return example.strip("\"")
            else:
                return "\"" + example

        def_examples = gloss.split("; \"")
        definition = def_examples[0].strip()
        examples = def_examples[1:]
        return (definition, map(remove_quotes, examples))
    #
    for synset, gloss in graph.subject_objects(WN_GLOSS):
        definition, examples = split_gloss(gloss)
        graph.add((synset, WN_DEFINITION, Literal(definition)))
        for example in examples:
            graph.add((synset, WN_EXAMPLE, Literal(example)))
    graph.remove((None, WN_GLOSS, None))
    return None


###
## add missing sense keys
WN_SENSEKEY = WN30["senseKey"]
WN_LEMMA = WN30["lemma"]
WN_LEXICOGRAPHER_FILE = WN30["lexicographerFile"]
WN_LEXICAL_ID = WN30["lexicalId"]
WN_SIMILAR_TO = WN30["similarTo"]

SYNSET_TYPE = {
    WN30["AdjectiveSynset"]: "3",
    WN30["NounSynset"]: "1",
    WN30["AdverbSynset"]: "4",
    WN30["AdjectiveSatelliteSynset"]: "5",
    WN30["VerbSynset"]: "2"
}

LEXICOGRAPHER_FILE_NUM = {"adj.all": 0,
"adj.pert": 1,
"adv.all": 2,
"noun.Tops": 3,
"noun.act": 4,
"noun.animal": 5,
"noun.artifact": 6,
"noun.attribute": 7,
"noun.body": 8,
"noun.cognition": 9,
"noun.communication": 10,
"noun.event": 11,
"noun.feeling": 12,
"noun.food": 13,
"noun.group": 14,
"noun.location": 15,
"noun.motive": 16,
"noun.object": 17,
"noun.person": 18,
"noun.phenomenon": 19,
"noun.plant": 20,
"noun.possession": 21,
"noun.process": 22,
"noun.quantity": 23,
"noun.relation": 24,
"noun.shape": 25,
"noun.state": 26,
"noun.substance": 27,
"noun.time": 28,
"verb.body": 29,
"verb.change": 30,
"verb.cognition": 31,
"verb.communication": 32,
"verb.competition": 33,
"verb.consumption": 34,
"verb.contact": 35,
"verb.creation": 36,
"verb.emotion": 37,
"verb.motion": 38,
"verb.perception": 39,
"verb.possession": 40,
"verb.social": 41,
"verb.stative": 42,
"verb.weather": 43,
"adj.ppl": 44,
"adjs.all": 45}

def add_missing_sensekeys(graph):
    for synset, sense in graph.subject_objects(WN_CONTAINS_WORDSENSE):
        if not (sense, WN_SENSEKEY, None) in graph:
            word = graph.value(sense, WN_WORD)
            lemma = graph.value(word, WN_LEMMA)
            assert lemma, sense
            for synset_type_uri in graph.objects(synset, RDF.type):
                # loop because RDF.type object might be either a POS
                # indicator or a core concept indicator
                synset_type = SYNSET_TYPE.get(synset_type_uri, None)
                if synset_type:
                    break
            lexicographer_file = graph.value(synset, WN_LEXICOGRAPHER_FILE)
            lexicographer_file_num = LEXICOGRAPHER_FILE_NUM[str(lexicographer_file)]
            assert synset_type and lexicographer_file, synset
            lexical_id = graph.value(sense, WN_LEXICAL_ID)
            assert lexical_id, sense
            head_lemma, head_lexical_id = "", ""
            head_sense = graph.value(sense, WN_SIMILAR_TO)
            if head_sense:
                head_word = graph.value(head_sense, WN_WORD)
                head_lemma = graph.value(head_word, WN_LEMMA)
                head_lexical_id = graph.value(head_sense, WN_LEXICAL_ID)
                assert head_lemma and head_lexical_id, head_sense
            sense_key = "{}%{}:{}:{}:{}:{}".format(lemma, synset_type,
                                                   lexicographer_file_num,
                                                   lexical_id, head_lemma,
                                                   head_lexical_id)
            graph.add((sense, WN_SENSEKEY, Literal(sense_key)))

###
## making the old RDF model closer to the current one: remove words,
## since they don't really exist in the text format
WN_WORD = WN30["word"]
WN_CONTAINS_WORDSENSE = WN30["containsWordSense"]
WN_LEXICAL_FORM = WN30["lexicalForm"]

def remove_words(graph):
    for synset, sense in graph.subject_objects(WN_CONTAINS_WORDSENSE):
        word = graph.value(sense, WN_WORD)
        assert word, sense
        lexical_form = graph.value(word, WN_LEXICAL_FORM)
        assert lexical_form, sense
        graph.add((sense, WN_LEXICAL_FORM, lexical_form))
    graph.remove((None, WN_WORD, None))
    return None
