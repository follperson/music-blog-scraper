#!/usr/bin/env python3
from parsers import Static
import re

FULLREPLACE = [re.compile('^None$'),re.compile('^\s*$')]
INLINE = {re.compile('\s*$'):'', re.compile('^\s*'):''}

class TextCleaners:
    class GenericCleaner:
        FULLREPLACE = FULLREPLACE
        INLINE = INLINE

    class BodyCleaner:
        INLINE = {'\xa0': ' ','\n':' '} # to strip characters in the body of the text
        FULLREPLACE = [re.compile('^Listen to the track below$',re.I),
                       re.compile('^Add to queue',re.I),re.compile('All rights reserved',re.I)] # to remove full text entries
    AbstractCleaner ={'list':{},
                      'str':{},
                    }

    PitchforkCleaner = {'list':{
                        Static.BODY: BodyCleaner},
                        'str': {},
    }
