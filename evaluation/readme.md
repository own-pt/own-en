Adding Python files that compare contributions and prepare files for Freeling evaluation

AssessingContributions106.ipynb ==> creates senses30Python.src; xwnPYTHON.dat; and locucionsPYTHON.dat (101 to 105 are previous versions/attempts and should be ignored). On a standard mac it takes 14 minutes to run. It processes all the changes in the noun.substance file (rocks and minerals). Still need to add geological times.

/usr/local/Cellar/freeling/4.1_3/share/freeling/en/senses30.dat ==> 2 columns table, senseID and term (PWN 3.0 id for d: and w:)

/usr/local/Cellar/freeling/4.1_3/share/freeling/common/xwn.dat ==> 2 columns table, senseID1 and senseID2 (PWN 3.0 id every pair w: and hypo/hyper/etc)

/usr/local/Cellar/freeling/4.1_3/share/freeling/en/locucions.dat ==>  auxiliary file for MWE identification

/usr/local/Cellar/freeling/4.1_3/share/freeling/en/dicc.src ==> add inflections (plural, etc). Use the following reference as a model (singular word NN for nouns singular):
limestone limestone NN
limestones limestone NNS
