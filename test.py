import pyhfst

input_stream = pyhfst.HfstInputStream("./analyser")
tr = input_stream.read()
print(tr.lookup("voi"))
print(tr.lookup("ihmettelen"))
print(tr.lookup("kissa"))
print(tr.lookup("koira"))
print(tr.lookup("koirani"))
print(tr.lookup("luutapiiri"))
print(tr.lookup("luutapiirissanikin"))
