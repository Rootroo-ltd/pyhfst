# Pyhfst

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7791470.svg)](https://doi.org/10.5281/zenodo.7791470)

Pyhfst is a pure Python implementation of HFST. The library makes it possible to use HFST optimized lookup FSTs without any C dependencies. Both weighted and unweighted FSTs are supported.

The library will run on all operting systems that support Python 3.

# Usage

    import pyhfst
    
    input_stream = pyhfst.HfstInputStream("./analyser")
    tr = input_stream.read()
    print(tr.lookup("voi"))
    
    >> [['voida+V+Act+Ind+Prs+Sg3', 0.0], ['voida+V+Act+Ind+Prs+ConNeg', 0.0], ['voida+V+Act+Ind+Prt+Sg3', 0.0], ['voida+V+Act+Imprt+Prs+ConNeg+Sg2', 0.0], ['voida+V+Act+Imprt+Sg2', 0.0], ['voi+N+Sg+Nom', 0.0], ['voi+Pcle', 0.0], ['voi+Interj', 0.0]]

# Citation

Please cite the library as follows:

Hämäläinen, Mika, & Alnajjar, Khalid. (2023). Pyhfst: A Pure Python Implementation of HFST (1.0.0). Zenodo. https://doi.org/10.5281/zenodo.7791470

    @article{pyhfst_2023, 
        title={Pyhfst: A Pure Python Implementation of HFST}, 
        DOI={10.5281/zenodo.7791470}, 
        publisher={Zenodo}, 
        author={Hämäläinen, Mika and Alnajjar, Khalid}, 
        year={2023} 
    }
