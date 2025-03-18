REQUISTI:
- Python
- Compilatore C++

INSTALLAZIONE:
- Scaricare la repository
- Nella cartella scaricata eseguire `pip install -r requirements.txt`

Configurazione 'FR3D':
- `cd fr3d-python`
- `python -m pip install .`

Configurazione 'RNAView':
- Command Prompt:
  - `setx RNAVIEW "percorso_cartella\RNAView-master"`
  - `setx PATH "%RNAVIEW%\bin;%PATH%"`
  - riavviare Command Prompt
- C shell (csh):
  - `nano ~/.cshrc`
  - aggiungere alla fine del file le seguenti 2 righe:
    - setenv RNAVIEW percorso_cartella/RNAView-master
    - setenv PATH "percorso_cartella/RNAView-master/bin:"$PATH
  - salvare le modifiche e chiudere
  - `source ~/.cshrc`
- Bourne shell (bash):
  - `nano ~/.bashrc`
  - aggiungere alla fine del file le seguenti 2 righe:
    - RNAVIEW=/percorso_cartella/RNAView-master; export RNAVIEW
    - PATH="/percorso_cartella/RNAView-master/bin:"$PATH; export PATH
  - salvare le modifiche e chiudere
  - `source ~/.bashrc`

UTILIZZO:
`python main.py "percorso cartella con file cif/percorso file di testo con pdb_id" -p <polimero>/-m <molecola> -t <tool>`

Valori disponibili polimero:
- r: polyribonucleotide (RNA)
- d: polydeoxyribonucleotide (DNA)
- h: polydeoxyribonucleotide/polyribonucleotide hybrid (IBRIDO)

Valori disponibili tool:
- f: FR3D
- r: RNAView

OUTPUT:
I file di output per ogni tool con il relativo bpseq si trovano nelle cartelle così definite:
- FR3D: fr3d/fr3d_bpseq
- RNAView: rnaview/rnaview_bpseq


