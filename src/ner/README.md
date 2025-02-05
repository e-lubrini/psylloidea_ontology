<h1 align="center">NER Corrections</h1>

This module contains:
- an analysis of the issues found during the application of the AlvisNLP NER tool on the PsylVe dataset;
- Improvements and contributions to the AlvisNLP tool.

## Directory Structure
    
    ner 
    └── psylve_addon_for_omnicrobe/         # to be copied in the reference pipeline (in this case, Omnicrobe)
    |   ├── psylve_versions/
    |   |       ├── psylve1.plan
    |   |       ├── psylve2.plan
    |   |       ├── psylve3.plan
    |   |       └── ...
    |   └── psylve_main.plan
    |
    └── data/
    |   ├── documents
    |   |   └── txt/
    |   └── preliminary_experiment.csv
    |
    └── launch.sh
    

## Usage

Move the content of the `psylve_addon_for_omnicrobe` to the `plan` directory in the [Omnicrobe](https://forgemia.inra.fr/omnicrobe/text-mining-workflow/) pipeline (`text-mining-workflow`).

`cd` to `psylve/src/ner_extraction/` directory and run the `launch.sh` script followed by a `-d` flag with the path to the text database for named entities to be extracted. The text documents must be in a child folder called `txt`.

### Example
#### file structure

        ├── text-mining-workflow/
        |        
        └── psylve/
            └── src/
                ├── ner/
                |   ├── data/
                |   |   └── documents/
                |   |       └── txt/
                |   |           ├── doc_1.txt
                |   |           ├── doc_2.txt
                |   |           ├── doc_3.txt
                |   |           └── ...
                |   |
                |   └── launch.sh
                ...

#### command
```bash
cd psylve/src/ner
bash launch.sh -d data/documents/
```
## Modules
- Correction Modules [README](https://github.com/e-lubrini/PsylVe/tree/internship/dataset_overview/README.md)


#### [◄ Back to main README](https://github.com/e-lubrini/PsylVe/tree/internship/README.md)
