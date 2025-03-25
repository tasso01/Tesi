REQUISTI:
- Python
- Compilatore C++
- Microsoft Visual C++

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

Configurazione 'Barnaba':
- `cd barnaba-master`
- `pip install .`

UTILIZZO:
`python main.py "percorso cartella con file cif/percorso file di testo con pdb_id" -p <polimero>/-m <molecola> -t <tool>`

Valori disponibili polimero:
- r: polyribonucleotide (RNA)
- d: polydeoxyribonucleotide (DNA)
- h: polydeoxyribonucleotide/polyribonucleotide hybrid (IBRIDO)

Valori disponibili tool:
- b: Barnaba
- f: FR3D
- r: RNAView

OUTPUT:
Le indicazioni su dove trovare all'interno del progetto gli output derivati dall'applicazione dei vari tool, si possono trovare nel file 'output.csv'



