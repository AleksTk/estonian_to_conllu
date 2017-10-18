from estnltk.vabamorf.morf import analyze
from estnltk import Text
import re
from dicts import *


def addtag(name, featdict, tag, word):
    if len(tag) != 0 and tag in featdict:
        word['featdict'][name] = featdict[tag]
    return word


def findfeats(word):
    word['featdict'] = {}

    # Abbr:
    word = addtag('Abbr', abbr, word['postag'], word)

    # AdpType - testing (low accuracy):
    if word['postag'] == 'K':
        word = addtag('AdpType', adptype, word['lemma'], word)

    # Case:
    if not (word['morf'] == 'n' and word['postag'] == 'V'):
        word = addtag('Case', case, word['morf'], word)

    # Connegative
    if 'chain' in word and word['postag'] == 'V' and word['morf'] != 'ma':
        if word['index'] in word['chain']['phrase'] and word['chain']['pol'] == 'NEG':
            if word['chain']['pattern'][word['chain']['phrase'].index(word['index'])] in ['ei', 'ega', 'ära', 'pole']:
                word['featdict']['Negative'] = 'Neg'
            elif word['chain']['pattern'][word['chain']['phrase'].index(word['index'])] not in ['&']:
                word['featdict']['Connegative'] = 'Yes'

    # Degree
    word = addtag('Degree', degree, word['postag'], word)

    # Foreign - not implemented

    # Hyph:
    if word['form'][-1] == '-' and len(word['form']) != 1:
        word['featdict']['Hyph'] = 'Yes'

    # Mood, testing chains:
    if not (word['morf'] == 'n' and word['postag'] != 'V'):
        word = addtag('Mood', mood, word['morf'], word)
    if 'chain' in word and word['postag'] == 'V':
        word = addtag('Mood', mood_chain, word['chain']['mood'], word)

    # Negative:
    word = addtag('Negative', negative, word['morf'], word)
    if word['lemma'] in ['ega', 'ära', 'mitte']:
        word['featdict']['Negative'] = 'Neg'
    if 'negative' in word['featdict'] and 'Connegative' in word['featdic']:
        del word['featdict']['Connegative']

    # Number:
    if not (word['morf'] == 'n' and word['postag'] != 'V'):
        word = addtag('Number', number, word['morf'], word)

    # NumForm - not implemented

    # NumType:
    word = addtag('NumType', numtype, word['postag'], word)

    # Person:
    if not (word['morf'] == 'n' and word['postag'] != 'V'):
        word = addtag('Person', person, word['morf'], word)
    if word['morf'] not in person and word['postag'] == 'P':
        word = addtag('Person', person_pron, word['lemma'], word)

    # Poss - not implemented

    # PronType - testing
    if word['postag'] == 'P':
        word = addtag('PronType', prontype, word['lemma'], word)

    # Reflex - testing
    if word['postag'] == 'P':
        word = addtag('Reflex', reflex, word['lemma'], word)

    # Tense, testing chains:
    if not (word['morf'] == 'n' and word['postag'] != 'V'):
        word = addtag('Tense', tense, word['morf'], word)
    if 'chain' in word and word['postag'] == 'V' and word['lemma'] != 'ei':
        if 'Tense' not in word['featdict']:
            word = addtag('Tense', tense_chain, word['chain']['tense'], word)

    # VerbForm, testing mood (which is testing chains):
    word = addtag('VerbForm', verbform, word['morf'], word)
    if 'VerbForm' not in word['featdict']:
        if word['postag'] == 'V' and 'Mood' in word['featdict']:
            word['featdict']['VerbForm'] = 'Fin'

    # Voice, testing chains:
    if not (word['morf'] == 'n' and word['postag'] != 'V'):
        word = addtag('Voice', voice, word['morf'], word)
    if 'chain' in word and word['postag'] == 'V' and word['lemma'] != 'ei':
        if word['chain']['voice'] == 'personal':
            word = addtag('Voice', voice_chain, word['chain']['voice'], word)

    if 'VerbForm' in word['featdict']:
        if word['featdict']['VerbForm'] == 'Inf':
            word['featdict'] = {'VerbForm': 'Inf'}

    return word


def findupostag(word):
    # Not entirely reliable as vabamorf does not provide universal POS tags,
    # so these are just brutal assumptions based on vabamorf POS tags.
    # However these tags do significantly improve parsing accuracy.
    #
    # Some notes on conversions:
    # Adverbs (D) - ADV (although there are a few exceptions tagging to ADJ in treebank)
    # Proper nouns (H) - PROPN (a few exceptions, for example ADJ)
    # Nouns (S) - NOUN (a few exceptions, for example ADJ)
    # Pronouns (P) - PRON although often serve as ADJ
    # Verbs (V) - VERB although could potentially be AUX
    # Not converted:
    # Abbreviations (Y) - no corresponding UPOS tag
    # Unclassified words that belong to VPs (X) - no corresponding UPOS tag
    # Conjunctions (J) - differentiation between CONJ and SCONJ is manually added

    if word['postag'] in uposdict:
        word['upostag'] = uposdict[word['postag']]
    elif word['postag'] == 'J' and word['lemma'] in conjdict:
        word['upostag'] = conjdict[word['lemma']]

    # AUX:
    if 'chain' in word and word['postag'] == 'V':
        if word['index'] in word['chain']['phrase']:
            if word['chain']['pattern'][word['chain']['phrase'].index(word['index'])] in ['ei', 'ära']:
                word['upostag'] = 'AUX'
            elif word['chain']['pattern'][word['chain']['phrase'].index(word['index'])] in ['pole', 'ole']:
                if len(word['chain']['phrase']) > 1:
                    if 'V_nud' in word['chain']['morph'] or 'V_tud' in word['chain']['morph']:
                        word['upostag'] = 'AUX'
            elif word['lemma'] in ['võima', 'tohtima', 'saama'] and 'V_da' in word['chain']['morph']:
                word['upostag'] = 'AUX'
            elif word['lemma'] in ['pidama'] and 'V_ma' in word['chain']['morph']:
                word['upostag'] = 'AUX'
            elif word['lemma'] in ['näima', 'paistma', 'tunduma'] and 'V_vat' in word['chain']['morph']:
                word['upostag'] = 'AUX'

    return word


def findxpostag(word):
    # UD treebank does not differentiate between some pos tags that vabamorf does:
    # proper nouns (H) are under common nouns (S)
    # adjectives in comparative (C) or superlative (U) are simply under adjectives (A)
    # ordinal numerals (O) are together with cardinal numerals (N)
    # there is a tag for foreign words (T) in the treebank which does not exist in vabamorf

    if word['postag'] in xposdict:
        word['xpostag'] = xposdict[word['postag']]

    return word


def autoanalyze(i, word, sentence, disambiguator):
    conll = ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc']

    word['id'] = str(i + 1)
    word['form'] = sentence.split()[i]

    word_data = disambiguator.disambiguate([sentence])[0]['words'][i]['analysis'][0]
    # the disambiguator tokenizes differently, therefore checking to make sure the same word is analyzed:
    if disambiguator.disambiguate([sentence])[0]['words'][i]['text'] != word['form']:
        word_data = analyze(word['form'])[0]['analysis'][0]

    word['postag'] = word_data['partofspeech']
    word['morf'] = word_data['form']
    word['lemma'] = word_data['lemma']
    word['root'] = word_data['root']

    word['index'] = i
    sentence_list = re.split('(?<=[.?!]) ', sentence)
    length = 0
    for option in sentence_list:
        length += len(option.split())
        if i < length:
            word['sentence'] = option
            break
        else:
            word['index'] -= length

    for chain in Text(word['sentence']).verb_chains:
        if i in chain['phrase']:
            word['chain'] = chain
            break

    word = findupostag(word)
    word = findxpostag(word)
    word = findfeats(word)

    word['feats'] = ''
    for key in sorted(word['featdict'].keys()):
        if word['feats'] == '':
            word['feats'] = key + '=' + word['featdict'][key]
        else:
            word['feats'] += '|' + key + '=' + word['featdict'][key]

    for tag in conll:
        if tag not in word or len(word[tag]) == 0:
            word[tag] = '_'

    line = '\t'.join([word['id'], word['form'], word['root'], word['upostag'], word['xpostag'], word['feats'],
                      word['head'], word['deprel'], word['deps'], word['misc']]) + '\n'

    return line
