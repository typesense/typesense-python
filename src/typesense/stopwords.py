from .stopwords_set import StopwordsSet


class Stopwords(object):
    RESOURCE_PATH = '/stopwords'

    def __init__(self, api_call):
        self.api_call = api_call
        self.stopwords_sets = {}

    def __getitem__(self, stopwords_set_id):
        if stopwords_set_id not in self.stopwords_sets:
            self.stopwords_sets[stopwords_set_id] = StopwordsSet(self.api_call, stopwords_set_id)

        return self.stopwords_sets.get(stopwords_set_id)

    def upsert(self, stopwords_set_id, stopwords_set):
        return self.api_call.put('{}/{}'.format(Stopwords.RESOURCE_PATH, stopwords_set_id), stopwords_set)

    def retrieve(self):
        return self.api_call.get('{0}'.format(Stopwords.RESOURCE_PATH))
