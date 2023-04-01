import pyhfst

input_stream = pyhfst.HfstInputStream("./analyser")
tr = input_stream.read()
print(tr.lookup("voi"))
print(tr.lookup("kissa"))