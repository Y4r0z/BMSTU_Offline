 
def stringCmp(original, toFind):
    if len(toFind) == 0:
        return True
    if original.lower().find(toFind) != -1 or invertString(original).find(toFind) != -1:
        return True
    return False

def stringFind(original, search):
    flag = True
    for word in search.split(' '):
        if not stringCmp(original, word):
            flag = False
    if not flag:
        inverted = invertString(search)
        flag = True
        for word in inverted.split(' '):
            if not stringCmp(original, word):
                flag = False
    return flag

def invertString(string):
    CyrillicTranslateAlphabet = dict(zip(list("qwertyuiop[]asdfghjkl;'zxcvbnm,."), list('йцукенгшщзхъфывапролджэячсмитьбю')))
    text = []
    for i in string:
        if i in CyrillicTranslateAlphabet.keys():
            text.append(CyrillicTranslateAlphabet[i])
        else:
            text.append(i)
    return ''.join(text)