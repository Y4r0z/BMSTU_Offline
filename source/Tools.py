 
def stringCmp(original, toFind):
    if len(toFind) == 0:
        return True
    CyrillicTranslateAlphabet = dict(zip(list("qwertyuiop[]asdfghjkl;'zxcvbnm,."), list('йцукенгшщзхъфывапролджэячсмитьбю')))
    if original.lower().find(toFind) != -1:
        return True
    else:
        text = []
        for i in toFind:
            if i in CyrillicTranslateAlphabet.keys():
                text.append(CyrillicTranslateAlphabet[i])
            else:
                text.append(i)
        if original.lower().find(''.join(text)) != -1:
            return True
    return False