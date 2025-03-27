# CT to X-Ray DRR Pipeline  

## Usage  
```bash
python pipeline.py -d <MAIN_DATA_DIR> -o <MAIN_OUTPUT_DIR> -c <CSV_PATH>
```

## Arguments
- -d → Path to the main data directory for a subset.

- -o → Path to the output directory where results will be stored.

- -c → Path to the annotations CSV file (annotations.csv) of the LUNA16 dataset.

## Example
```bash
python pipeline.py -d /path/to/data -o /path/to/output -c /path/to/annotations.csv
```

## Code for jupyter notebook
```bash
!git clone https://github.com/ThatBlackFox/Luna16-Extractor.git
%cd Luna16-Extractor
!pip install -r requirements.txt
!python pipeline -d <Subset DIR> -o <OUTPUT DIR> -c <ANNOTATIONS_PATH>
```
