import itertools as it
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import re
import pandas as pd

filter_str_list = []
def draw_labeled_multigraph(G, attr_name, ax=None):


    connectionstyle = [f"arc3,rad={r}" for r in it.accumulate([0.8]* 40)]

    pos = nx.shell_layout(G)

    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=100)
    nx.draw_networkx_labels(G, pos, font_size=10, ax=ax)
    nx.draw_networkx_edges(
        G, pos, edge_color="grey", connectionstyle=connectionstyle, ax=ax
    )


    labels = {
        tuple(edge): f"{attr_name}={attrs[attr_name]}"
        for *edge, attrs in G.edges(keys=True, data=True)
    }
    nx.draw_networkx_edge_labels(
        G,
        pos,
        labels,
        connectionstyle=connectionstyle,
        label_pos=0.8,
        font_color="blue",
        font_size = 4,
        bbox={"alpha": 0},
        ax=ax,
    )
def style_log_lines(df, filename):
    queryList = []
    redisQueryList = []
    extraInfo = []
    majorNodes = []
    labels = ['start']
    splitted_list = []
    index = 0
    for line in df.iterrows():
        if 'OrderProcessingSideEffect' in line[1][0]:
            logNumber = str(index + 1)
            cline = '::' + logNumber + '::' + '::'.join(line[1].values.astype(str))
            extraInfo.append('***' + logNumber + '***' + cline.split('\n')[0].split('::')[2])
            if cline.split('\n')[0].split('::')[1] not in labels:
                labels.append(cline.split('\n')[0].split('::')[1])
            if len(majorNodes) > 0:
                tupInd = -1
                for i, (first, second) in enumerate(queryList):
                    if cline.split('\n')[0].split('::')[4] in second:
                        tupInd = i
                        continue
                if tupInd == -1:
                    queryList.append((str(index + 1), cline.split('\n')[0].split('::')[4]))
                    pair = ()
                    if cline.split('\n')[0].split('::')[3] == 'Database':
                        pair = (majorNodes[index - 1][1], 'dq' + str(index + 1))
                    elif cline.split('\n')[0].split('::')[3] == 'Redis':
                        pair = (majorNodes[index - 1][1], 'redisq' + str(index + 1))
                    elif cline.split('\n')[0].split('::')[3] == 'RabbitMq':
                        pair = (majorNodes[index - 1][1], 'rabbitq' + str(index + 1))
                    elif cline.split('\n')[0].split('::')[3] == 'Business':
                        pair = (majorNodes[index - 1][1], 'business' + str(index + 1))
                    else:
                        pair = (majorNodes[index - 1][1], cline.split('\n')[0].split('::')[3])
                    majorNodes.append(pair)
                else:
                    pair = ()
                    if cline.split('\n')[0].split('::')[3] == 'Database':
                        pair = (majorNodes[index - 1][1], 'dq' + str(tupInd if tupInd > -1 else index + 1))
                    elif cline.split('\n')[0].split('::')[3] == 'Redis' and 'dcrc' not in cline.split('\n')[0].split('::')[4]:
                        pair = (majorNodes[index - 1][1], 'redisq' + str(tupInd if tupInd > -1 else index + 1))
                    elif cline.split('\n')[0].split('::')[3] == 'RabbitMq':
                        pair = (majorNodes[index - 1][1], 'rabbitq' + str(index + 1))
                    elif cline.split('\n')[0].split('::')[3] == 'Business':
                        pair = (majorNodes[index - 1][1], 'business' + str(index + 1))
                    else:
                        pair = (majorNodes[index - 1][1], cline.split('\n')[0].split('::')[3])
                    majorNodes.append(pair)

            else:
                pair = ()
                if cline.split('\n')[0].split('::')[3] == 'Database':
                    pair = ('start', 'dq' + str(index + 1))
                elif cline.split('\n')[0].split('::')[3] == 'Redis' and 'dcrc' not in cline.split('\n')[0].split('::')[4]:
                    pair = ('start', 'redisq' + str(index + 1))
                elif cline.split('\n')[0].split('::')[3] == 'RabbitMq':
                    pair = ('start', 'rabbitq' + str(index + 1))
                elif cline.split('\n')[0].split('::')[3] == 'Business':
                    pair = ('start', 'business' + str(index + 1))
                else:
                    pair = ('start', cline.split('\n')[0].split('::')[3])

                majorNodes.append(pair)
            cline = cline.replace('#', '\n#')
            if 'dcrc' not in cline.split('\n')[0].split('::')[4]:
                splitted_list.append(cline.split('\n'))

            # filtered_list = [item for item in splitted_list if
            #                  not any(filter_str.lower() in item.lower() for filter_str in filter_str_list)]
            # cline = '\n'.join(filtered_list)
            # styled_line = '' + cline.strip() + '\n\n'
            # output_file.write(styled_line)
            # output_file.write('=' * 80 + '\n')
            index += 1

    write_to_file(filename, splitted_list)
    return majorNodes
def is_null_or_empty(string):
    return string.strip() is None or string.strip() == ''
def filter_log_lines(input_file_path):
    repetitive_info = []
    total_major_nodes = []
    duplicate_major_nodes = []
    filtered_major_nodes = []
    with open(input_file_path, 'r', encoding='utf-8') as input_file:

        split_data = [i.split('::') for i in input_file]
        df = pd.DataFrame(split_data)
        criterion = df[df.columns[0]].str.contains('OrderProcessingSideEffect')
        filtered_df = df[criterion]
        duplicates = filtered_df[filtered_df.duplicated(2, keep=False)]
        total_major_nodes = style_log_lines(df, 'total.log')
        duplicate_major_nodes = style_log_lines(duplicates, 'duplicates.log')
        filtered_major_nodes = style_log_lines(filtered_df, 'filtered.log')
        return (total_major_nodes, duplicate_major_nodes, filtered_major_nodes)

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


major_nodes_list = filter_log_lines('dev.log')

fig, ax = plt.subplots()
G = nx.MultiDiGraph()
for i, (u, v) in enumerate(major_nodes_list[1]):
    G.add_edge(u, v, f= i + 1)
pos = nx.spring_layout(G, k=0.5, iterations=500)


draw_labeled_multigraph(G, "f", ax)
ax.set_title('Order Processing Flow Scenario 1')

fig.tight_layout()
plt.figure(figsize=(800, 600))

fig.show()
fig.savefig("plot.svg")
