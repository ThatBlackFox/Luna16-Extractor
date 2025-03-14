# CT Patch Extractor - Help

## Usage:
  python dataset_maker.py -d <data_directory> -o <output_directory> [-c <csv_file>]<br>

## Options:
  -d    Path to the directory containing full chest CT scans (.mhd)  [Required]<br>
  -o    Output directory to store extracted CT patches                [Required]<br>
  -c    Path to the CSV file containing annotations (optional)<br>

## Example Usage:
  python dataset_maker.py -d /path/to/ct_scans -o /path/to/output <br>
  python dataset_maker.py -d /path/to/ct_scans -o /path/to/output -c annotations.csv

## Description:
  This script extracts patches from chest CT scans stored in the specified directory.<br>
  If an annotation CSV file is provided, patches will be extracted based on its coordinates.<br>
  Else the script expects an annotation CSV file in the data directory.
