import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
import numpy as np

from utilities.make_domains_list import file_to_int_list

def pie_chart_maker(csv_file_path, output_path, vulnerable_ports_csv_file):
    df2 = pd.read_csv(vulnerable_ports_csv_file)
    # df2 = pd.read("./vulenrable_ports.csv")
    vulnerable_port = df2['vul_ports'].tolist()
    vulnerable_colours = df2['colour_code'].tolist()
    print(vulnerable_colours)
    print(vulnerable_port)
    final_colours = []
    # vulnerable_port = file_to_int_list(vulnerable_ports_file)
    
    df = pd.read_csv (csv_file_path)
    group_by_diag = df.groupby("open port").count().reset_index()
    sizes = list(group_by_diag['subdomain'])
    labels = list(group_by_diag['open port'])
    overall = sum(sizes)
    new_sizes = []
    new_labels = []
    bar_others_labels = []
    bar_others_size = []
    new_size = 0
    for i in range(0,len(labels)):
        port = labels[i]
        if(port not in vulnerable_port):
            new_size = new_size + sizes[i]
            bar_others_labels.append("Port: " + str(port))
            bar_others_size.append(sizes[i])
        else:
            new_labels.append(port)
            new_sizes.append(sizes[i]/overall)
            final_colours.append(vulnerable_colours[vulnerable_port.index(port)])

    if(new_size == 0):
        print(csv_file_path, " , Case 1")
        fig, (ax1) = plt.subplots(1, figsize=(15, 10))
        overall_ratios = new_sizes
        labels = []
        for label in new_labels:
            labels.append("Port: " + str(label))
        angle = -180 * overall_ratios[0]
        p = plt.pie(overall_ratios, autopct='%1.1f%%', startangle=angle,
                        labels=labels, colors=final_colours)
        plt.title('Pie Chart for IP enumeration and Port scan (Ports scanned = ' + str(sum(sizes)) + ')')
        plt.legend()
        plt.savefig(output_path)


    # make figure and assign axis objects
    else:
        print(csv_file_path, " , Case 2")
        # print("jrnfsenadsj")
        new_sizes.insert(0, new_size/overall)
        new_labels.insert(0,"others")
        final_colours.insert(0,"#F3ECEC")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 10))
        fig.subplots_adjust(wspace=0)
        # pie chart parameters
        overall_ratios = new_sizes
        labels = []
        for label in new_labels:
            labels.append("Port: " + str(label))
        # labels = new_labels
        explode = [0.1]
        for i in range(1,len(new_labels)):
            explode.append(0)
        # rotate so that first wedge is split by the x-axis
        # print(overall_ratios)
        angle = -180 * overall_ratios[0]
        # print(angle)
        p = ax1.pie(overall_ratios, autopct='%1.1f%%', startangle=angle,
                            labels=labels, explode=explode, colors=final_colours)
        wedges = p[0]

        ax1.set_title('Pie Chart for IP enumeration and Port scan (Ports scanned = ' + str(sum(sizes)) + ')')
        ax1.legend()
        # bar chart parameters
        age_ratios = []
        for i in bar_others_size:
            age_ratios.append(i/new_size)
        # age_ratios = bar_others_size
        age_labels = bar_others_labels
        bottom = 1
        width = .2

        # Adding from the top matches the legend.
        for j, (height, label) in enumerate(reversed([*zip(age_ratios, age_labels)])):
            bottom -= height
            bc = ax2.bar(0, height, width, bottom=bottom, label=label,)
            ax2.bar_label(bc, labels=[f"{height:.0%}"], label_type='center')

        ax2.set_title('Other ports')
        ax2.legend()
        ax2.axis('off')
        ax2.set_xlim(- 2.5 * width, 2.5 * width)

        # use ConnectionPatch to draw lines between the two plots
        theta1, theta2 = wedges[0].theta1, wedges[0].theta2
        center, r = wedges[0].center, wedges[0].r
        bar_height = 1

        # draw top connecting line
        x = r * np.cos(np.pi / 180 * theta2) + center[0]
        y = r * np.sin(np.pi / 180 * theta2) + center[1]
        con = ConnectionPatch(xyA=(-width / 2, bar_height), coordsA=ax2.transData,
                            xyB=(x, y), coordsB=ax1.transData)
        con.set_color([0, 0, 0])
        con.set_linewidth(1)
        ax2.add_artist(con)

        bar_bottom_height = bar_height - sum(age_ratios)
        # draw bottom connecting line
        x = r * np.cos(np.pi / 180 * theta1) + center[0]
        y = r * np.sin(np.pi / 180 * theta1) + center[1]
        con = ConnectionPatch(xyA=(-width / 2, bar_bottom_height), coordsA=ax2.transData,
                            xyB=(x, y), coordsB=ax1.transData)
        con.set_color([0, 0, 0])
        ax2.add_artist(con)
        con.set_linewidth(1)

        plt.savefig(output_path)
    
    
# csv_file_path = 'csv_file.csv'

# pie_chart_maker(csv_file_path, "./foo.png", "./utilities/vulnerable_ports.csv")
