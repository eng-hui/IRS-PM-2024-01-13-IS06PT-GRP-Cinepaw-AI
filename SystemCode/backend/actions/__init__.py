from actions.search import query_tmdb, convert_tmdb_to_mvlen


class Action(object):
    def __init__(self):
        pass

    def execute(self, *args, **kwargs):
        # actual execute part
        pass

    def desc(self):
        # return text to describe the action to 
        pass