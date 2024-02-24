# Pyhfst

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7791470.svg)](https://doi.org/10.5281/zenodo.7791470)

Pyhfst is a pure Python implementation of HFST. The library makes it possible to use HFST optimized lookup FSTs without any C dependencies. Both weighted and unweighted FSTs are supported.

The library will run on all operting systems that support Python 3.

# Installation

    pip install pyhfst
    
Pyhfst can run way faster if you have Cython installed. After installing Cython, you must reinstall Pyhfst

    pip install cython
    pip install --upgrade --force-reinstall pyhfst --no-cache-dir

# Usage

    import pyhfst
    
    input_stream = pyhfst.HfstInputStream("./analyser")
    tr = input_stream.read()
    print(tr.lookup("voi"))
    
    >> [['voida+V+Act+Ind+Prs+Sg3', 0.0], ['voida+V+Act+Ind+Prs+ConNeg', 0.0], ['voida+V+Act+Ind+Prt+Sg3', 0.0], ['voida+V+Act+Imprt+Prs+ConNeg+Sg2', 0.0], ['voida+V+Act+Imprt+Sg2', 0.0], ['voi+N+Sg+Nom', 0.0], ['voi+Pcle', 0.0], ['voi+Interj', 0.0]]

# Citation

Please cite the library as follows:

Alnajjar, K., & Hämäläinen, M. (2023, December). PYHFST: A Pure Python Implementation of HFST. In Lightning Proceedings of NLP4DH and IWCLUL 2023 (pp. 32-35).

    @article{pyhfst_2023, 
        title={PyHFST: A Pure Python Implementation of HFST},
        author={Alnajjar, Khalid and H{\"a}m{\"a}l{\"a}inen, Mika},
        booktitle={Lightning Proceedings of NLP4DH and IWCLUL 2023},
        pages={32--35},
        year={2023} 
    }
