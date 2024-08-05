#*****************************************************************#
###Title                            Emo PS Image File Selection
###Purpose                          selects specific files
###                                 from sets 1,2 and 3 of
###                                 emotional images according to
###                                 criteria and outputs them to
###                                 New sets A,B, and C in folders
###Creation Date                    07/01/2021
###Created by                       Derek V. Taylor
###Last Modified                    08/11/2021
#*****************************************************************#


from datetime import datetime
import os
from os import path
from os import listdir
from os.path import isfile, join
import sys
import pandas as pd
import glob
import shutil


def main():
    try:
        error_log = "Data Parsed, Error Occured During, Record, Notes" + "\n"
        error_level = ""
        tpath = join("/","tmp","yassapublic","Experiments","Closed_Enrollment","Various_Projects","Emotional_PS_Short",
                "emotional_mdt_a","stimuli")
        error_level = "Precleaning,remove old folders,"
        for F in glob.glob(tpath +"/*"):
            fname = get_file_name(F)
            if fname in ['setA', 'setB', 'setC']:
                for ofile in (glob.glob(F +"/*.jpg")):
                    os.remove(ofile)
        error_level = "Building File List, Binding Glob,"
        df_files = pd.DataFrame(glob.glob(tpath +"/*/*.jpg"))
        error_level = "Building File dataframe, Naming columns,"
        df_files.columns = ['pname']
        error_level = "Building File dataframe, getting filename,"
        df_files.loc[:, 'fname'] = df_files['pname'].apply(get_file_name)
        error_level = "Building File dataframe, Naming columns,"
        df_files.loc[:, 'sfolder'] = df_files['pname'].apply(get_folder_name)
        error_level = "Building File dataframe, Getting filetype,"
        df_files.loc[:, 'ftype'] = df_files['fname'].apply(get_file_type)
        error_level = "Building File dataframe,Getting file subtype,"
        df_files.loc[:, 'subtype'] = df_files['fname'].apply(get_file_subtype)
        df_files = df_files.sort_values(by=['sfolder', 'ftype', 'subtype', 'fname'],
                                        ascending=(True, True, True, False))
        df_files.loc[:,'filecount'] = df_files.groupby(['sfolder', 'ftype' , 'subtype']).cumcount()
        df_types = df_files.groupby(by=['sfolder', 'ftype', 'subtype']).agg({'filecount': 'max'})
        df_files.loc[:, 'new_set'] = 0
        df_files.loc[(df_files['ftype'] == 'foils') & (df_files['subtype'] ==
                     'F-Neg') & (df_files['filecount'] < 5), 'new_set'] = 1
        df_files.loc[(df_files['ftype'] == 'foils') & (df_files['subtype'] ==
                     'F-Neu') & (df_files['filecount'] < 5), 'new_set'] = 1
        df_files.loc[(df_files['ftype'] == 'foils') & (df_files['subtype'] ==
                     'F-Pos') & (df_files['filecount'] < 5), 'new_set'] = 1
        error_level = "Select New Dataset, select repeats"
        df_files.loc[(df_files['ftype'] == 'repeats') & (df_files['subtype'] ==
                     'R-Neg') & (df_files['filecount'] < 5), 'new_set'] = 1
        df_files.loc[(df_files['ftype'] == 'repeats') & (df_files['subtype'] ==
                     'R-Neu') & (df_files['filecount'] < 5), 'new_set'] = 1
        df_files.loc[(df_files['ftype'] == 'repeats') & (df_files['subtype'] ==
                     'R-Pos') & (df_files['filecount'] < 5), 'new_set'] = 1
        df_files.loc[(df_files['ftype'] == 'lure') & (df_files['filecount'] > 10) &
                     (df_files['filecount'] < 21), 'new_set'] = 1
        df_files.loc[(df_files['ftype'] == 'Encoding') & (df_files['filecount'] > 10) &
                     (df_files['filecount'] < 31), 'new_set'] = 1
        error_level = "subset image sets, selecting all where new set is true,"
        df_new_files = df_files.loc[(df_files['new_set'] == 1)]
        error_level = "subset image sets, using apply to create datasets,"
        df_new_files.loc[:, 'copied'] = df_new_files['pname'].apply(copy_sets)
        error_level = "subset image sets, add sim to new set,"
        df_new_files.loc[:, 'sim'] = df_new_files['fname'].apply(get_sim)
        df_new_files.loc[:, 'arousal'] = df_new_files['fname'].apply(get_aroused)
        error_level = "subset image sets, Get new Count of file types including sim,"
        df_types = df_new_files.groupby(by=['sfolder', 'ftype', 'subtype', 'sim']).agg({'filecount': 'count'})
        error_level = "subset image sets, Get new Count of file types including arousal,"
        df_types = df_new_files.groupby(by=['sfolder', 'ftype', 'subtype', 'arousal']).agg({'filecount': 'count'})
        error_level = "subset image sets, using apply to create datasets,"
    except:
        error_log = error_log + error_level + ',' + str(sys.exc_info()[1]) + '\n'
    print(error_log)


def get_file_name(pname):
    parts = pname.split('/')
    end = len(parts)-1
    fname = parts[end]
    return fname


def get_folder_name(pname):
    parts = pname.split('/')
    end = len(parts)-2
    sfolder = parts[end]
    return sfolder


def get_file_type(fname):
    fname = fname.replace('.jpg','')
    if 'a' in fname:
        ftype = 'Encoding'
    elif ('b' in fname) or ('c' in fname) or ('d' in fname) or ('e' in fname):
        ftype = 'lure'
    elif fname[0] in ["4", "5", "6"]:
        ftype = "repeats"
    elif fname[0] in ["7", "8", "9"]:
        ftype = 'foils'
    return ftype


def get_file_type(fname):
    fname = fname.replace('.jpg', '')
    if 'a' in fname:
        ftype = 'Encoding'
    elif ('b' in fname) or ('c' in fname) or ('d' in fname) or ('e' in fname):
        ftype = 'lure'
    elif fname[0] in ["4", "5", "6"]:
        ftype = "repeats"
    elif fname[0] in ["7", "8", "9"]:
        ftype = 'foils'
    return ftype


def get_file_subtype(fname):
    if fname[0] == "1":
        subtype = 'Neg-Lure'
    elif fname[0] == "2":
        subtype = 'Neut-Lure'
    elif fname[0] == "3":
        subtype = 'Pos-Lure'
    elif fname[0] == "4":
        subtype = 'R-Neg'
    elif fname[0] == "5":
        subtype = 'R-Neu'
    elif fname[0] == "6":
        subtype = 'R-Pos'
    elif fname[0] == '7':
        subtype = "F-Neg"
    elif fname[0] == '8':
        subtype = "F-Neu"
    elif fname[0] == '9':
        subtype = "F-Pos"
    else:
        subtype = "lure"
    return subtype

def get_sim(fname):
    fname = fname.replace('.jpg', '')
    if ('b' in fname) or ('d' in fname):
        sim = 'LOW'
    elif ('c' in fname) or ('e' in fname):
        sim = 'HIGH'
    else:
        sim = 'not'
    return sim


def copy_sets(fpath):
    try:
        if 'set1' in fpath:
            dest = fpath.replace('set1', 'setA')
        elif 'set2' in fpath:
            dest = fpath.replace('set2', 'setB')
        elif 'set3' in fpath:
            dest = fpath.replace('set3', 'setC')
        shutil.copyfile(fpath, dest, follow_symlinks=True)
        return 1
    except:
        return 0


def get_aroused(fname):
    fname = fname.replace('.jpg', '')
    if 'a' in fname:
        fname = fname.replace('a', '')
    elif 'b' in fname:
        fname = fname.replace('b', '')
    elif 'c' in fname:
        fname = fname.replace('c', '')
    elif 'd' in fname:
        fname = fname.replace('d', '')
    elif 'e' in fname:
        fname = fname.replace('e', '')
    fact = int(fname[0])
    num = int(fname)
    result = num - fact*10000
    if result <= 25:
        arousal = 'LOW'
    elif result > 25:
        arousal = "HIGH"
    else:
        arousal = 'none'
    return arousal


if __name__ == '__main__':
    main()
