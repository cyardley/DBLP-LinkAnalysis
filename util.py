import sys

def sprint(x):
    sys.stdout.write(str(x))
    sys.stdout.flush()

def sortReverse(lst):
    srt = sorted(lst)
    rlst = srt[: :-1]
    return rlst

#This function is copied from:
#http://code.activestate.com/recipes/252143-invert-a-dictionary-one-liner/
def dictinvert(d):
    inv = {}
    for k, v in d.iteritems():
        keys = inv.setdefault(v, [])
        keys.append(k)
    return inv
