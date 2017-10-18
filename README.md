Script for automatically tagging Estonian text according to CoNLL-U standard using the morphological analysis from EstNLTK's Vabamorf integration.

Requisites:
- Python 3
- EstNLTK

Running:
./analyze.py --input someinput.txt --output someoutput.txt [--conll]

Input files should be tokenized, one token per line and an empty line after each sentence. It is also possible to use CoNLL files as input to reanalyze them (use the flag --conll).
