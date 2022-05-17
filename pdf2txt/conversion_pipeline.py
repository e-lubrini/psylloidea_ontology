#!/bin/bash

#############
## IMPORTS ##
#############
import functools
import subprocess
import sys

from tools.utils import *
from tools.conv_tools import *
from tools import conv_tools as ctools

##############
## PIPELINE ##
##############
subprocess.Popen(['echo', 'conversion starting...'])

input_dir_path = sys.argv[1]
dbg(sys.argv[1])

# if there are any imgs, convert them to pdf
not_pdf_filepaths = list_ext(input_dir_path,    # files to be converted to pdf
                            exts=['pdf'],
                            invert=True,
                            )
map(functools.partial(ctools.img2pdf,           # convert to pdf
                    input_dir_path_path=input_dir_path),
    not_pdf_filepaths)      

pdf_filepaths = list_ext(input_dir_path,        # all pdf files
                        exts=['pdf'],
                        invert=False,
                        )

# rearrange folder structure
for pdf_filepath in pdf_filepaths:
    mv_to_custom_dir(pdf_filepath)

# compile metadata for each file
for dir_path in get_child_dir_paths(input_dir_path):
    metadata = write_pdf_metadata(path=dir_path,
                                metadata_lab=['emb_txt',
                                            'lang_codes'],
                                )
# if file has embedded text, extract it with grobid
    if metadata['emb_txt']:
        #pdf2xml(dir_path)
        pass
# convert file to text with ocr
    pdf2txt(dir_path,
            tool_names=['pytesseract_ocr'],
            tools=get_funs_from_module(ctools),
            save_in_dir=True,
            overwrite=True,
            )

# translate text to English
for dir_path in get_child_dir_paths(input_dir_path):
    translate_doc(dir_path)

subprocess.Popen(['echo', 'conversion successful!'])