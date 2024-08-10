import itertools as it
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import re
import pandas as pd

filter_str_list = []

def style_log_lines(df, filename):
    extraInfo = []
    majorNodes = []

    splitted_list = []
    index = 0
    for line in df.iterrows():
        if 'OrderProcessingSideEffect' in line[1][0]:
            logNumber = str(index + 1)
            cline = '::' + logNumber + '::' + '::'.join(line[1].values.astype(str))
            extraInfo.append('***' + logNumber + '***' + cline.split('\n')[0].split('::')[2])

            cline = cline.replace('#', '\n#')
            if 'dcrc' not in cline.split('\n')[0].split('::')[4]:
                splitted_list.append(cline.split('\n'))

            index += 1

    write_to_file(filename, splitted_list)
    return majorNodes
def is_null_or_empty(string):
    return string.strip() is None or string.strip() == ''
def read_logs_from_file(input_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        split_data = [i.split('::') for i in input_file]
        df = pd.DataFrame(split_data)
        criterion = df[df.columns[0]].str.contains('OrderProcessingSideEffect')
        filtered_df = df[criterion]
        return filtered_df


def write_to_file(output_file_path, splitted_list):
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        cline = ''
        for line in splitted_list:

            filtered_list = [item for item in line if
                     not any(filter_str.lower() in item.lower() for filter_str in filter_str_list)]
            cline += '\n'.join(filtered_list) + '\n'
            cline += '=' * 80
            cline += '\n'

        styled_line = '' + cline.strip() + '\n\n'
        extract_flow(styled_line)
        output_file.write(styled_line)
        output_file.write('=' * 80 + '\n')


def extract_flow(styled_line):
    with open('flow_file.log', 'w', encoding='utf-8') as flow_file:
        result = []
        for line in styled_line.split('=' * 80):
            documentOutCome = line.replace('\n', '')
            index = 0
            sepResult = [part.strip() for part in
             documentOutCome.split('::') if
             'called at' in part]
            if len(sepResult) > 0 :
                segmentHasArrow = False
                for segment in re.split(r'\#\d+\:', sepResult[0]):
                    if is_null_or_empty(segment) == False and index < 3:
                        if 'called at' in segment:
                            res = re.split('called at', segment)
                            # if '->' in res[0] :
                            segmentHasArrow = True
                            result.append(documentOutCome.split('::')[3] + '::' + documentOutCome.split('::')[4])
                            result.append(res[0] + ' ' + re.split('/', res[1])[-1])

                            index += 1
                if segmentHasArrow == True:
                    result.append('=' * 80)
        flow_file.write('\n'.join(result))

df_new_logs = read_logs_from_file('dev.log')
style_log_lines(df_new_logs, 'new_style_log_lines.log')
df_new_logs = df_new_logs.drop([3, 4, 5], axis=1)

df_old_logs = read_logs_from_file('old-dev.log')
style_log_lines(df_old_logs, 'old_style_log_lines.log')
df_old_logs = df_old_logs.drop([3, 4, 5], axis=1)


result = df_new_logs.equals(df_old_logs)
differences = df_new_logs.compare(df_old_logs)
print(result)
print(differences)



