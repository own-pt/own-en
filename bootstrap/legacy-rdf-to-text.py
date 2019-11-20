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
WN_LANG = WN30["lang"]

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
"adj.ppl": 44}

def add_missing_sensekeys(graph):
    for synset, sense in graph.subject_objects(WN_CONTAINS_WORDSENSE):
        if (synset, WN_LANG, Literal("en")) in graph:
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
        word = graph.value(sense, WN_WORD, any=False)
        assert word, sense
        lexical_form = graph.value(word, WN_LEXICAL_FORM)
        assert lexical_form, sense
        graph.add((sense, WN_LEXICAL_FORM, lexical_form))
    for word in set(graph.objects(None, WN_WORD)):
        graph.remove((word, None, None))
        graph.remove((None, None, word))
    return None

###
## add fake source_begin info, for sorting
WN_SOURCE_BEGIN = WN30["sourceBegin"]

def add_source_begin(graph):
    def synset_minimal_wordsense(synset):
        wordsenses = graph.objects(synset, WN_CONTAINS_WORDSENSE)
        word_forms = list(map(lambda ws: graph.value(ws, WN_LEXICAL_FORM), wordsenses))
        if None in word_forms or not word_forms:
            print(synset)
        min_word_form = min(word_forms)
        return min_word_form
    #
    graph.remove((None, WN_SOURCE_BEGIN, None))
    lexicographer_files = set(graph.objects(predicate=WN_LEXICOGRAPHER_FILE))
    for lexicographer_file in lexicographer_files:
        sorted_synsets = sorted(graph.subjects(WN_LEXICOGRAPHER_FILE, lexicographer_file), key=synset_minimal_wordsense)
        for ix, synset in enumerate(sorted_synsets):
            graph.add((synset, WN_SOURCE_BEGIN, Literal(ix)))
    return None

###
## add frames
FRAMES_TO_ID = {
    "Something ----s": Literal(1),
    "Somebody ----s": Literal(2),
    "It is ----ing": Literal(3),
    "Something is ----ing PP": Literal(4),
    "Something ----s something Adjective/Noun": Literal(5),
    "Something ----s Adjective/Noun": Literal(6),
    "Somebody ----s Adjective": Literal(7),
    "Somebody ----s something": Literal(8),
    "Somebody ----s somebody": Literal(9),
    "Something ----s somebody": Literal(10),
    "Something ----s something": Literal(11),
    "Something ----s to somebody": Literal(12),
    "Somebody ----s on something": Literal(13),
    "Somebody ----s somebody something": Literal(14),
    "Somebody ----s something to somebody": Literal(15),
    "Somebody ----s something from somebody": Literal(16),
    "Somebody ----s somebody with something": Literal(17),
    "Somebody ----s somebody of something": Literal(18),
    "Somebody ----s something on somebody": Literal(19),
    "Somebody ----s somebody PP": Literal(20),
    "Somebody ----s something PP": Literal(21),
    "Somebody ----s PP": Literal(22),
    "Somebody's (body part) ----s": Literal(23),
    "Somebody ----s somebody to INFINITIVE": Literal(24),
    "Somebody ----s somebody INFINITIVE": Literal(25),
    "Somebody ----s that CLAUSE": Literal(26),
    "Somebody ----s to somebody": Literal(27),
    "Somebody ----s to INFINITIVE": Literal(28),
    "Somebody ----s whether INFINITIVE": Literal(29),
    "Somebody ----s somebody into V-ing something": Literal(30),
    "Somebody ----s something with something": Literal(31),
    "Somebody ----s INFINITIVE": Literal(32),
    "Somebody ----s VERB-ing": Literal(33),
    "It ----s that CLAUSE": Literal(34),
    "Something ----s INFINITIVE": Literal(35),
}

WN_FRAME = WN30["frame"]

def use_frame_numbers(graph):
    for subj, frame in graph.subject_objects(WN_FRAME):
        frame_id = FRAMES_TO_ID[frame.strip()]
        graph.remove((subj, WN_FRAME, frame))
        graph.add((subj, WN_FRAME, frame_id))
    return None
