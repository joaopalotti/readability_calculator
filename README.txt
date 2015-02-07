======================
Readability Calculator
======================

Readability calculator is a simple program to estimate how skilled a reader must be to understand a piece of text.
There is a large number of methods for that. The following ones are implemented in the current version of this program:

    1. `Flesh Reading Ease <http://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_test#Flesch_Reading_Ease>`_
    2. `Flesh Kincaid Grade Level <http://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_Grade_Level#Flesch.E2.80.93Kincaid_Grade_Level>`_
    3. `Coleman Liau Index <http://en.wikipedia.org/wiki/Coleman-Liau_Index>`_
    4. `Gunning Fog Index <http://en.wikipedia.org/wiki/Gunning-Fog_Index>`_
    5. `SMOG Index <http://en.wikipedia.org/wiki/SMOG>`_
    6. `ARI Index <http://en.wikipedia.org/wiki/Automated_Readability_Index>`_
    7. `LIX Index <http://en.wikipedia.org/wiki/LIX>`_
    8. `Dale-Chall Score <http://en.wikipedia.org/wiki/Dale%E2%80%93Chall_readability_formula>`_

Usage
-----

    #!/usr/bin/env python
    
    from readcalc import readcalc

    calc = readcalc.ReadCalc("This is a simple text.")

    print calc.get_smog_index()

