'''

*****************************************************************
Title                           Emo PS Data
Purpose                         Assmebles data from log files int
                                single table in repeated measurs
                                analysis format and exports to
                                file
Creation Date                   08/01/2021
Created by                      Derek V. Taylor
Last Modified                   08/16/2021
*****************************************************************

'''

from datetime import datetime
import os
from statsmodels.stats.anova import AnovaRM
from os import path
from os import listdir
from os.path import isfile, join
import sys
import pandas as pd
import glob
import shutil
import argparse

def main():
    error_log = "Data Parsed, Error Occured During, Record, Notes" + '\n'
    error_level = ""
    try:
        error_level = "Get Parameters, Declare Arg Parser,"
        parser = argparse.ArgumentParser()
        error_level = "Get Parameters, Add arguments to parser,"
        parser.add_argument('-s', required=True, help="Log Files Folder")
        parser.add_argument('-d', required=True, help="Output folder for Results")
        error_level = "Get Parameters, Run Args Parser,"
        args = parser.parse_args()
        error_level = "Get Parameters, Declare Arg Parser,"
        source = args.s
        rfound = 0
        dest = args.d
        if path.exists(source):
            error_level = "Pre-cleaning,remove old folders,"
            rpt_dict = get_rpt_dictionary()
            for F in glob.glob(source + "/*.txt"):
                error_level = "File iteration, Save any previous file data,"
                if rfound > 0:
                    error_level = "Saving data, add found items to dictionary,"
                    df_rpt_row = pd.DataFrame(rpt_dict, index=[0])
                    if rfound == 1:
                            df_rpt = df_rpt_row
                    elif rfound > 1:
                        df_rpt = df_rpt.append(df_rpt_row)
                    rpt_dict = get_rpt_dictionary()
                error_level = "File Parsing,Get File_name,"
                digitime = os.path.getmtime(F)
                rpt_dict['dititime'] = digitime
                File_Create = datetime.fromtimestamp(os.path.getmtime(F))
                rpt_dict['File_Create'] = File_Create
                fname = get_file_name(F)
                error_level = "File Parsing,Get File_name,"
                IDParts = fname.split('_')
                ID = IDParts[0]
                rpt_dict['ID'] = ID
                Set = IDParts[1]
                rpt_dict['Set'] = Set
                with open(F, 'r') as mfile:
                    log_data = mfile.readlines()
                for l in log_data:
                    l = l.strip()
                    if "LDI-Negative Low Sim" in l:
                        ivar = l.split(':')[1]
                        ivar = ivar.strip()
                        LDI_Neg_Low_Sim = float(ivar)
                        rpt_dict['LDI_Neg_Low_Sim'] = LDI_Neg_Low_Sim
                        rfound += 1
                    elif "LDI-Negative High Sim" in l:
                        ivar = l.split(':')[1]
                        ivar = ivar.strip()
                        LDI_Neg_High_Sim = float(ivar)
                        rpt_dict['LDI_Neg_High_Sim'] = LDI_Neg_High_Sim
                    elif "LDI-Neutral Low Sim" in l:
                        ivar = l.split(':')[1]
                        ivar = ivar.strip()
                        LDI_Neut_Low_Sim = float(ivar)
                    elif "LDI-Neutral High Sim" in l:
                        ivar = l.split(':')[1]
                        ivar = ivar.strip()
                        LDI_Neut_High_Sim = float(ivar)
                        rpt_dict['LDI_Neut_High_Sim'] = LDI_Neut_High_Sim
                    elif "LDI-Positive Low Sim" in l:
                        ivar = l.split(':')[1]
                        ivar = ivar.strip()
                        LDI_Pos_Low_Sim = float(ivar)
                    elif "LDI-Positive High Sim" in l:
                        ivar = l.split(':')[1]
                        ivar = ivar.strip()
                        LDI_Pos_High_Sim = float(ivar)
                        rpt_dict['LDI_Pos_Low_Sim'] = LDI_Pos_Low_Sim
                    elif "LDI-Negative Collapsed" in l:
                        ivar = l.split(':')[1]
                        ivar = ivar.strip()
                        LDI_Neg_Collapsed = float(ivar)
                        rpt_dict['LDI_Neg_Collapsed'] = LDI_Neg_Collapsed
                    elif "LDI-Neutral Collapsed" in l:
                        ivar = l.split(':')[1]
                        ivar = ivar.strip()
                        LDI_Neut_Collapsed = float(ivar)
                        rpt_dict['LDI_Neut_Collapsed'] = LDI_Neut_Collapsed
                    elif "LDI-Positive Collapsed" in l:
                        ivar = l.split(':')[1]
                        ivar = ivar.strip()
                        LDI_Pos_Collapsed = float(ivar)
                        rpt_dict['LDI_Pos_Collapsed'] = LDI_Pos_Collapsed
                    elif "RecMem-Neg" in l:
                        ivar = l.split(':')[1]
                        ivar = ivar.strip()
                        RecMem_Neg = float(ivar)
                        rpt_dict['RecMem_Neg'] = RecMem_Neg
                    elif "RecMem-Neu" in l:
                        ivar = l.split(':')[1]
                        ivar = ivar.strip()
                        RecMem_Neu = float(ivar)
                        rpt_dict['RecMem_Neu'] = RecMem_Neu
                    elif "RecMem-Pos" in l:
                        ivar = l.split(':')[1]
                        ivar = ivar.strip()
                        RecMem_Pos = float(ivar)
                        rpt_dict['RecMem_Pos'] = RecMem_Pos
                error_level = "Pre-cleaning,remove old folders,"
        error_level = "Data Processing, append last row,"
        if rfound > 1:
            df_rpt_row = pd.DataFrame(rpt_dict, index=[0])
            df_rpt = df_rpt.append(df_rpt_row)
        error_level = "Data Processing, order by ID and date,"
        df_rpt_r = df_rpt.sort_values(by=['ID', 'File_Create', 'Set'])
        error_level = "Data Processing, Create count of ,"
        df_rpt_r['inst'] = df_rpt_r.groupby(['ID']).cumcount()+1
        error_level = "Data Processing, order by ID and date,"
        df_rpt_r = df_rpt_r.loc[(df_rpt_r['inst'] < 3)]
        #df_rpt_m = pd.merge(df_rpt.loc[df_rpt['inst']==1], df_rpt.loc[df_rpt['inst']==2], on=['ID'])
        error_level = "Data Processing, order by ID and date,"
        depvars = "LDI_Neg_Low_Sim,LDI_Neg_High_Sim,LDI_Neut_High_Sim,LDI_Pos_Low_Sim,LDI_Neg_Collapsed," \
                      "LDI_Neut_Collapsed,LDI_Pos_Collapsed,RecMem_Neg,RecMem_Neu,RecMem_Pos"
        depvars = depvars.split(',')
        print("Analysis By Order\n\n")
        for items in depvars:
            print("Evaluating: ", items)
            print(AnovaRM(data=df_rpt_r, depvar=items, subject='ID', within=['inst']).fit())
        error_level = "Data Processing, order by ID and Set,"
        df_rpt_s = df_rpt.sort_values(by=['ID', 'Set'])
        error_level = "Data Processing, Create count of ,"
        df_rpt_s['inst'] = df_rpt_s.groupby(['ID']).cumcount()+1
        error_level = "Data Processing, order by ID and date,"
        df_rpt_s = df_rpt_s.loc[(df_rpt_s['inst'] < 3)]
        #df_rpt_m = pd.merge(df_rpt.loc[df_rpt['inst']==1], df_rpt.loc[df_rpt['inst']==2], on=['ID'])
        error_level = "Data Processing, order by ID and date,"
        depvars = "LDI_Neg_Low_Sim,LDI_Neg_High_Sim,LDI_Neut_High_Sim,LDI_Pos_Low_Sim,LDI_Neg_Collapsed," \
                      "LDI_Neut_Collapsed,LDI_Pos_Collapsed,RecMem_Neg,RecMem_Neu,RecMem_Pos"
        depvars = depvars.split(',')
        print("\n\n\nAnalysis By Set")
        for items in depvars:
            print("Evaluating: ", items)
            print(AnovaRM(data=df_rpt_s, depvar=items, subject='ID', within=['inst']).fit())
        df_diff = df_rpt.groupby(by=['Set']).agg({'LDI_Neg_High_Sim': ['mean','std']})
        print(df_diff.head)
    except:
        error_log = error_log + error_level +    ',' + str(sys.exc_info()[1]) + '\n'
    print(error_log)


def get_rpt_dictionary():
    try:
        rpt_headers = "ID,Set,digitime,File_Create,LDI_Neg_Low_Sim,LDI_Neg_High_Sim,LDI_Neut_High_Sim,LDI_Pos_Low_Sim,LDI_Neg_Collapsed," \
                      "LDI_Neut_Collapsed,LDI_Pos_Collapsed,RecMem_Neg,RecMem_Neu,RecMem_Pos"
        rpt_dic = rpt_headers.replace(',', '= '' ,') + '='''
        rpt_dic = dict(x.split("=") for x in rpt_dic.split(','))
        return rpt_dic
    except:
        return None


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


if __name__ == '__main__':
    main()
