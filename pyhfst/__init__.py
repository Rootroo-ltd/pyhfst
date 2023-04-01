from .hfst_optimized_lookup import HfstOptimizedLookup

class HfstInputStream(object):
	"""docstring for ClassName"""
	def __init__(self, path):
		self.path = path

	def read(self):
		t= HfstOptimizedLookup()
		tr = t.main([self.path])
		return Hfst(tr)

class Hfst(object):
	def __init__(self, tr):
		self.tr = tr
	def lookup(self, string):
		return [["".join(_r.get_symbols()), _r.get_weight()] for _r in self.tr.analyze(string)]
		