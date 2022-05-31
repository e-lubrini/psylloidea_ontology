#!/usr/bin/python3.10

from curses import meta
from gettext import translation
from importlib.metadata import metadata
from inspect import getmembers, isfunction
import functools
from nis import match
import os
import string

import json

import fitz
import fasttext
fasttext.FastText.eprint = lambda x: None

import enchant
from enchant.checker import SpellChecker
from enchant.errors import DictNotFoundError, DefaultLanguageNotFoundError

from tqdm import tqdm

from nltk.corpus import words
from nltk.tokenize import sent_tokenize
import nltk
#nltk.download('words')

from deep_translator import GoogleTranslator

from time import sleep
import inspect
import functools

import subprocess

import tools.eval_tools as etools
from tools.eval_tools import eval_tools_scores

###########
## DEBUG ##
###########
def get_var_name(var):
    try:
        callers_local_vars = inspect.currentframe().f_back.f_back.f_locals.items()
        var = [var_name for var_name, var_val in callers_local_vars if var_val is var][0]
    except IndexError:
        callers_local_vars = inspect.currentframe().f_back.f_locals.items()
        var = [var_name for var_name, var_val in callers_local_vars if var_val is var][0] 
    return str(var)

def dbg(mess, title=''):
    #subprocess.Popen(['echo', str('\033[35m'+ str(title)+'\033[32m'+ str(get_var_name(mess)+': '+'\033[0m'+str(mess)))])
    print(str('\033[35m'+ str(title)+'\033[32m'+ str(get_var_name(mess)+': '+'\033[0m'+str(mess))))
    return

def verbose_mess(mess, verbose):
    if verbose:
        mess_col(mess, verbose)

colours = dict(black = "30m",
                red = "31m",
                green = "32m",
                yellow = "33m",
                blue = "34m",
                magenta = "35m",
                cyan = "36m",
                white = "37m",
                grey = "38m",
                )

def mess_col(mess, col_tag, colours=colours):
    print('\033[0;{0} {1}. \033[0m'.format(col_tag, mess))
    return

#############
## GENERAL ##
#############
# human readable size
def hr_size(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def get_funs_from_module(module):
    funs_raw = getmembers(module,isfunction)
    funs = dict()
    for n,t in funs_raw:
        funs[n] = t
    return funs

def true_counter(funcQ, elems, **kwargs):
    c = sum([funcQ(e,**kwargs) for e in tqdm(elems, get_var_name(elems))])
    return c

def try_read(path, ext=None, alt=''):
    try:
        if ext is None:
            filepath = path
        else:
            filepath = get_child_ext_path(path, ext)
        with open(filepath) as f:
            content = f.read()
    except (IndexError, FileNotFoundError):
        content = alt
    return content

def store_data(storage,
                data,
                dir_path,
                name):
    storage_types = ['meta', # the metadata file
                    'dir'] # a new subdirectory where the document is stored
    if storage not in storage_types:
        raise ValueError("Invalid path_type. Expected one of: {0}".format(storage_types)) 
    
    if data:
        match storage:
            case 'meta':
                data_path = os.path.join(dir_path,name+'.json')
                with open(data_path, 'w+') as f:
                    json.dump(data, f)
            case 'dir':
                if type(data) == dict:
                    for k,v in data.items():
                        
                        new_dir = mkdir_no_over(os.path.join(dir_path,k))
                        data_path = os.path.join(new_dir, name+'.txt')
                        with open(data_path, 'w+') as f:
                            f.write(v)   
                else:
                    new_dir = mkdir_no_over(os.path.join(dir_path,name))
                    data_path = os.path.join(new_dir, get_var_name(data)+'.txt')
                    with open(data_path, 'w+') as f:
                        f.write(data)
    else:
        data_path = ''
    return data_path


#######################
## PATH MANIPULATION ##
#######################
def get_dir_and_doc_paths(path):
    if os.path.isfile(path):
        dir_path = get_parent_dir(path)
        filepath = path
    elif os.path.isdir(path):
        dir_path = path
        filepath = get_child_ext_path(dir_path=dir_path, ext='pdf')
    else:
        print('enter an existing path')
    return dir_path, filepath

def join_parentpath_childnames(parentpath,childnames):
    fullpaths = map(functools.partial(os.path.join,
                        parentpath),
        childnames)
    return list(fullpaths)


# lists paths with certain extension 
def list_ext(path,
            exts,
            invert=False): # return files WITHOUT such extensions instead
    path_list = list()
    for ext in exts:
        if type(ext) == list:
            ext = ext[0]
        for filename in os.listdir(path):
            filepath = os.path.join(path,filename)
            ends_ext = filepath.endswith(ext)
            is_file = os.path.isfile(filepath)
            has_ext = ends_ext and is_file
            if not invert:
                ret_ext = has_ext 
                if ret_ext:
                    path_list.append(filepath)
            elif is_file:
                ret_ext = not has_ext
                if ret_ext:
                    path_list.append(filepath)
    return path_list

# get one child with requested extension
def get_child_ext_path(dir_path, ext):
    child = list_ext(path=dir_path,exts=[ext])[0]
    return child

# creates a folder with the document's name and moves the document in it
def mv_to_custom_dir(doc_path):
    split_path = os.path.split(doc_path)
    ext = os.path.splitext(doc_path)[-1]
    new_dir_name = split_path[-1][:-len(ext)] # same as filename, without the extension
    filename = split_path[-1]
    input_dir_path = split_path[-2]

    new_dir_path = os.path.join(input_dir_path,new_dir_name.replace(" ", "_"))
    new_doc_path = os.path.join(new_dir_path,filename.replace(" ", "_"))

    if not os.path.exists(new_dir_path):
        os.mkdir(new_dir_path)
    if not os.path.exists(new_doc_path):
        os.rename(doc_path,new_doc_path)
    else:
        print('Warning: a document named {0} already exists. Deleting the newer copy.'.format(filename))
        os.remove(doc_path)
    return
def get_parent_dir(path):
    return os.path.split(path)[-2]

def get_child_dir_paths(dir_path):
    child_names = os.listdir(dir_path)
    child_paths = [os.path.join(dir_path,child_name) for child_name in child_names]
    dir_paths = [child_path for child_path in child_paths if os.path.isdir(child_path)]
    return dir_paths

# make directory if it doesn't exist
def mkdir_no_over(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    return dir_name
    
def save_file(filepath, data):
    with open(filepath, 'w+') as f:
        f.write(data)

def save_data(doc_dir,
                dir_name,
                file_name,
                content,
                ):
    dirpath = os.path.join(doc_dir,dir_name)
    mkdir_no_over(dir_name)
    filepath = os.path.join(dirpath,file_name)
    save_data(filepath, content)
    

###############
## PDF TOOLS ##
###############
# extract embedded text
def get_emb_txt(path):
    _, doc_path = get_dir_and_doc_paths(path)
    try:
        metadata = read_doc_metadata(path=doc_path, path_type='doc')
        text = metadata['emb_text']
    except:
        text = ""
        doc = fitz.open(doc_path)
        for page in doc:
            text += page.get_text()
    return text

# tokenise and preprocess text
def prep_and_tokenise(text):
    doc_wordlist = list(set(text.translate(str.maketrans('', '', string.punctuation)).lower().replace('\n',' ').split()))
    prep_text = ' '.join(doc_wordlist).replace('\n',' ')
    return prep_text, doc_wordlist

# find language(s) of a text
def get_langs(prep_text,     # text whose language is to be detected
            lang_n=1    # how many possible lang_codes we want to detect (in order from most to least probable)
            ):
    model = fasttext.load_model(os.path.join('models','lid.176.ftz'))
    prediction = (model.predict(prep_text, k=lang_n))[0] # tuple of language codes and respective probabilities
    lang_codes = [label[-2:] for label in prediction]
    return lang_codes    # list of language code(s) detected

                
##############
## METADATA ##
##############
def write_pdf_metadata(path, overwrite_keys):
    dir_path, filepath = get_dir_and_doc_paths(path)
    # info to be stored
    metadata = get_metadata(filepath, overwrite_keys)
    # write metadata file
    meta_path = os.path.join(dir_path, 'metadata.json')
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent = 4)
    return metadata

def get_meta_path(path, path_type):
    path_types = ['doc', # the document being treated
                'meta', # the metadata file
                'dir'] # the directory where the metadata is stored
    if path_type not in path_types:
        raise ValueError("Invalid path_type. Expected one of: {0}".format(path_types)) 
    match path_type:
        case 'doc': 
            dir_path = os.path.split(path)[-2]
            meta_path = get_child_ext_path(dir_path, '.json')
        case 'meta':
            meta_path = path
        case 'dir':
            dir_path = path
            meta_path = get_child_ext_path(dir_path, '.json')
    return meta_path

def read_doc_metadata(path, path_type):
    meta_path = get_meta_path(path, path_type=path_type)
    with open(meta_path) as f:
        metadata = json.load(f)
    return metadata

def get_metadata(dir_path,
                storage_opts,
                overwrite_opts,
                threshold,
                ):
    try:
        meta_path = get_meta_path(dir_path, path_type='dir')
        with open(meta_path) as f:
            metadata = json.load(f)
    except (IndexError, FileNotFoundError):
        metadata = dict()

    metadata['emb_txt'] = get_emb_txt(dir_path)
    if storage_opts['lang_codes'] and (overwrite_opts['lang_codes'] or not ('lang_codes' in metadata.keys())):
        prep_txt,_ = prep_and_tokenise(metadata['emb_txt'])
        metadata['lang_codes'] = get_langs(prep_txt)
    
    pop_keys = set()
    for k in metadata.keys():
        pop_keys.add if k not in storage_opts.keys() else None
    for k in pop_keys:
        metadata.pop(k, None)

    # check if emb text is usable
    if storage_opts['emb_txt_ok'] and (overwrite_opts['emb_txt_ok'] or not ('emb_txt_ok' in metadata.keys())):
        metadata['score'] = eval_tools_scores(db_dir_path=dir_path,
                                                text=metadata['emb_txt'], # tools to be evaluated
                                                score_names=['spellcheck_score'],
                                                scoring_funs= get_funs_from_module(etools),
                                                )['spellcheck_score']
        metadata['emb_txt_ok'] = metadata['score'] >= threshold

    return metadata
    

# add metadata entry
def add_metadata_entry(dir_path,
                        entry_name,
                        entry_cont,
                        ):
    metadata = read_doc_metadata(dir_path, path_type='dir')
    meta_path = get_meta_path(dir_path, path_type='dir')
    metadata[entry_name] = entry_cont
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent = 4)

####################
## LANGUAGE TOOLS ##
####################
def translate_to_lang(txt,
                source_lang_code,
                targ_lang_code,
                ):
    sents = sent_tokenize(txt)
    trans_sents = list()
    for sent in tqdm(sents, desc='translated sentences', leave=False):
        try:
            trans_sent = str((GoogleTranslator(source_lang_code,targ_lang_code).translate(str(sent))))
        except:
            trans_sent = str(sent)
        trans_sents.append(trans_sent)
    translation = ' '.join(trans_sents)
    return translation

# get translation if needed
def get_translation(tool_dir_path,
                    source_text,
                    source_lang_code,
                    targ_lang_code,
                    storage_opts,
                    overwrite_opts,
                    ):
    src_type = get_var_name(source_text)
    translation = try_read(os.path.join(tool_dir_path, 'translation.txt'))
    needs_trans = storage_opts[src_type+'_trans'] and (overwrite_opts[src_type+'_trans'] or not translation)
    if needs_trans:
        translation = translate_to_lang(source_text,
                                        source_lang_code=source_lang_code,
                                        targ_lang_code=targ_lang_code,
                                        )
    return translation