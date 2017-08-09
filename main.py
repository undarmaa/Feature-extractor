import numpy as np


class BtcTransformer(object):
    """
    This class performs string -> feature map transformation.
    Feed it numpy.ndarray of data + labels with shape [[string1', label1],
                                                       ... ,
                                                       [stringN', labelN]]
    """
    __slots__ = ['arr', 'labels', 'catcols', 'cache']

    def __init__(self, array):
        if type(array) == np.ndarray:
            self.arr = array
        elif type(array) == list:
            self.arr = np.array(array)
        self.labels = array[:, -1]
        self.catcols = None
        self.cache = []

    def fit_transform(self):
        features = self.extract_feats()
        r, c = features.shape
        try:
            error = 1 in self.catcols
        except TypeError:
            print('"Categorical columns" array is empty')
            exit()

        for col in self.catcols:
            z = sum([1 if i == 0 else 0 for i in features[:, col]])
            o = sum([1 if i == 1 else 0 for i in features[:, col]])
            try:
                l0 = sum([1 if features[i, col] == 0 and self.labels[i] == '1' else 0 for i in range(r)]) / z
            except ZeroDivisionError:
                l0 = 0.
            try:
                l1 = sum([1 if features[i, col] == 1 and self.labels[i] == '1' else 0 for i in range(r)]) / o
            except ZeroDivisionError:
                l1 = 0.

            self.cache.append([l0, l1])

            for el in range(r):
                features[el, col] = l0 if features[el, col] == 0 else l1
        return features

    def transform(self):
        pass

    def feature_extractor(self, st):
        """
        for input 'string' forming feature array with columns:
        1) 24 < len < 35
        2) starts with '1', '3' or '0'
        3) contains only: - lowercase
        4) - uppercase
        5) - digits
        6) attitude of symbols in [a..f] and [g..z]
        7) attitude lowers/uppers
        8) some letter repeats more than 3 times in a row
        9) any lettering of length 4 appears more than 1 time
        """
        result = []
        letters = list(st)
        length = len(st)

        # if 24 < len < 35?
        q = 1 if (24 < length < 35) else 0
        result.append(q)
        # print('len ', q)

        # does the string start with 0, 1 or 3?
        q = 1 if (letters[0] == '1' or letters[0] == '3' or letters[0] == '0') else 0
        result.append(q)
        # print('start ', q)

        # counting different symbols
        lowers = 0
        uppers = 0
        digits = 0
        inA_F = 0
        inG_Z = 0
        for letter in letters:
            if letter.islower():
                lowers += 1
            elif letter.isupper():
                uppers += 1
            elif letter.isdigit():
                digits += 1
            if letter.lower() in 'abcdef':
                inA_F += 1
            elif letter.lower() in 'ghijklmnopqrstuvwxyz':
                inG_Z += 1
        q = 1 if lowers == length - digits else 0
        result.append(q)
        q = 1 if uppers == length - digits else 0
        result.append(q)
        q = 1 if digits == length else 0
        result.append(q)
        # print('counts')
        try:
            q = inA_F / inG_Z
        except ZeroDivisionError:
            q = .0
        # print('zerodivs ', q)
        result.append(q)
        try:
            q = lowers / uppers
        except ZeroDivisionError:
            q = .0
        result.append(q)
        # print('zerodivs ', q)
        # does the repeating appear in str?
        w = 3
        j = 0
        count = 0
        using = letters[0]
        for i in letters:
            count += 1
            if using == i:
                j += 1
            else:
                j = 0
                using = i
            if j > w:
                result.append(1)
                # print('find 1')
                break
            if count == length - 1:
                result.append(0)
                # print('not find 1')
                break

        full = ''.join(a for a in letters)
        # print(full)
        count = 0
        for i in range(length - 3):
            count += 1
            string = ''.join(a for a in letters[i: i +4])
            if full.find(string) != full.rfind(string):
                result.append(1)
                # print('find 2')
                break
            if count == length - 3:
                result.append(0)
                # print('not find 2')
                break
        return result

    def extract_feats(self):
        feats = []
        for s in self.arr:
            a = self.feature_extractor(s)
            feats.append(a)
        feats = np.array(feats)
        unique = []
        for i in range(feats.shape[1]):
            unique.append(len(np.unique(feats[:, i])))
        self.catcols = [i for i, j in enumerate(unique) if j == 2]

        return feats
