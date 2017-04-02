import re
import nltk


class NaturalLanguageProcessor:
    def __init__(self):
        self.cached_stop_words = nltk.corpus.stopwords.words('English')
        self.word_net_lemmatizer = nltk.stem.WordNetLemmatizer()

    def extract_user_name_from_text(self, input_text):
        google_cloud_result = []
        if len(input_text) == 0:
            return google_cloud_result
        google_cloud_result = self._match_name_from_template(input_text.lower())
        if len(google_cloud_result) == 0:
            google_cloud_result = self._get_human_names(input_text)
        if len(google_cloud_result) == 0:
            regex = re.compile('([A-Z]\w+(?=[\s\-][A-Z])(?:[\s\-][A-Z]\w+)+)',
                               re.UNICODE)
            google_cloud_result = regex.findall(input_text)
        if len(google_cloud_result) == 0:
            google_cloud_result.append(input_text)
        return google_cloud_result

    def refractor_tokens_to_spoken_string(self, token):
        text = ''
        l = len(token)
        if l == 1:
            text = text + token[0]
            return text
        for i in range(0, l - 1):
            text += ','
            text = text + token[i]
        text += ' and '
        text = text + token[l - 1]
        text = text[1:]
        return text

    def remove_stop_words(self, word_list):
        filtered_words = [word for word in word_list if word not in self.cached_stop_words]
        return filtered_words

    def _match_name_from_template(self, s):
        p = re.compile(r'(?:name is|i am|i\'m|call me|this is) (.*)')
        return p.findall(s)

    def _get_human_names(self, text):
        tokens = nltk.tokenize.word_tokenize(text)
        pos = nltk.pos_tag(tokens)
        sentt = nltk.ne_chunk(pos, binary=False)
        person_list = []
        person = []
        name = ""
        for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
            for leaf in subtree.leaves():
                person.append(leaf[0])
            for part in person:
                name = name + part + ' '
            if name[:-1] not in person_list:
                person_list.append(name[:-1])
            name = ''
            person = []
        return person_list

    def remove_stop_words_dict(self, dict_freq):
        del_list = []
        for key in dict_freq:
            if key in self.cached_stop_words:
                del_list.append(key)
        for item in del_list:
            del dict_freq[item]
        return dict_freq

    def construct_bigrams(self, unigrams):
        bigrams = []
        if len(unigrams) < 2:
            return bigrams
        for i in range(1, len(unigrams)):
            bigrams.append(unigrams[i - 1] + unigrams[i])
        return bigrams

    def get_singular(self, word):
        lemma = self.word_net_lemmatizer.lemmatize(word, 'n')
        plural = True if word is not lemma else False
        return plural, lemma

    def construct_trigrams(self, unigrams):
        trigrams = []
        if len(unigrams) < 3:
            return trigrams
        for i in range(2, len(unigrams)):
            trigrams.append(unigrams[i - 2] + unigrams[i - 1] + unigrams[i])
        return trigrams



