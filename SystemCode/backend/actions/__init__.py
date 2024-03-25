from actions.search import query_movie_db


class Action(object):
	def __init__(self):
        pass

    def execute(self, *args, **kwargs):
        # actual execute part
        pass

    def desc(self):
        # return text to describe the action to 
        pass