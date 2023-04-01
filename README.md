# Pyhfst

Pyhfst is a pure Python implementation of HFST. The library makes it possible to use HFST optimized lookup FSTs without any C dependencies. Both weighted and unweighted FSTs are supported.

The library will run on all operting systems that support Python 3.

# Usage

    import pyhfst
    
    input_stream = pyhfst.HfstInputStream("./analyser")
    tr = input_stream.read()
    print(tr.lookup("voi"))
    
    >> [['voida+V+Act+Ind+Prs+Sg3', 0.0], ['voida+V+Act+Ind+Prs+ConNeg', 0.0], ['voida+V+Act+Ind+Prt+Sg3', 0.0], ['voida+V+Act+Imprt+Prs+ConNeg+Sg2', 0.0], ['voida+V+Act+Imprt+Sg2', 0.0], ['voi+N+Sg+Nom', 0.0], ['voi+Pcle', 0.0], ['voi+Interj', 0.0]]
