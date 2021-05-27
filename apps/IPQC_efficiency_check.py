import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import itertools
from math import ceil


def get_database(root):
    pathss = []
    for file in os.listdir(root):
        if "FAI_IPQC" in file and '~$' not in file:  # 只处理该路径下的Excel文件
            pathss.append(root+file)

    data = pd.DataFrame()
    for file in pathss:
        df = pd.read_excel(file, index_col='FAI_IPQC_time', usecols=[
                           'FAI_IPQC_time', 'IPQC_2_start', 'measure_2_finish', 'Whole_time'])
        data = pd.concat([data, df])

    return data


def get_data(database, range_dates):
    time_format = '%Y-%m-%d'
    start_date = pd.to_datetime(str(range_dates[0]), format=time_format)
    end_date = pd.to_datetime(
        str(range_dates[1]), format=time_format) + pd.Timedelta(hours=23, minutes=59)

    # # extract the FAI data within the period
    mask = (database.index > start_date) & (database.index <= end_date)
    data_in_duration = database.loc[mask]

    return data_in_duration


def get_df_at_different_duration(data, precision):
    df_union = []
    # df_single = pd.DataFrame()
    name_list = []
    for timing, df in data.resample(precision):
        df.dropna(how='all', inplace=True)
        if len(df.index):
            name_list.append(timing)
            df_union.append(df)

    return df_union, name_list


def FAI_IPQC_reviewby_day(data):
    # Read in data & create total column
    stacked_bar_data = data.loc[:, 'IPQC_2_start':'Whole_time']
    the_range = list(range(stacked_bar_data.shape[0]))  # range number
    fig, ax = plt.subplots()
    # Set general plot properties
    # sns.set_context({"figure.figsize": (10, 5)})

    ax = sns.barplot(x=the_range,
                     y=stacked_bar_data.Whole_time, color="brown")
    sns.set_style("white")

    # Plot 2 - overlay - "bottom" series
    bottom_plot = sns.barplot(ax=ax, x=the_range,
                              y=stacked_bar_data.IPQC_2_start, color="gray")
    topbar = plt.Rectangle((0, 0), 1, 1, fc="brown", edgecolor='none')
    bottombar = plt.Rectangle((0, 0), 1, 1, fc='gray',  edgecolor='none')

    l = plt.legend([bottombar, topbar], ['IPQC_2_start', 'measure_2_finish'],
                   loc=1, ncol=1, prop={'size': 12})
    l.draw_frame(False)

    # #Optional code - Make plot look nicer
    sns.despine(left=True)
    bottom_plot.set_ylabel("Duration (hrs)")
    bottom_plot.set_xlabel("Day time")

    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False)  # labels along the bottom edge are off

    # Set fonts to consistent 16pt size
    for item in ([bottom_plot.xaxis.label, bottom_plot.yaxis.label] +
                 bottom_plot.get_xticklabels() + bottom_plot.get_yticklabels()):
        item.set_fontsize(16)

    st.pyplot(fig)


def another_way_of_stack(data):
    fig, ax = plt.subplots()
    length = np.arange(len(data.index))
    ax.bar(length, data['IPQC_2_start'], label='IPQC_2_start', color='brown')
    ax.bar(length, data['measure_2_finish'],
           bottom=data['IPQC_2_start'], label='measure_2_finish', color='gray')
    plt.tick_params(axis='x', which='both',  bottom=False, top=False, labelbottom=False)
    plt.legend()
    st.pyplot(fig)


def barchart_of_whole_IPQC_time(data):
    fig, ax = plt.subplots()
    ax = sns.histplot(data=data.Whole_time)
    ax.set_xlabel('IPQC to measure finished (Hrs)')
    ax.set_ylabel('Counts')
    ax.set_ylabel('Hrs')
    st.pyplot(fig)


def data_of_whole_time(data):
    df_whole_time = pd.DataFrame()
    # name_list = []
    for timing, df in data.resample('D'):
        df = df['Whole_time']
        df.dropna(how='all', inplace=True)
        if len(df.index):
            # name_list.append(timing)
            df.reset_index(inplace=True, drop=True)
            df.name = str(timing)[:10]
            df_whole_time = pd.concat([df_whole_time, df], axis=1)

    return df_whole_time


def boxplot_of_whole_time(whole_data):
    fig, ax = plt.subplots()
    ax = sns.boxplot(data=whole_data)
    ax = sns.swarmplot(data=whole_data, color=".5", size=4.5)
    ax.set_ylabel('Hrs')
    st.pyplot(fig)


def app():

    root = 'database/'
    database = get_database(root)

    range_dates = st.sidebar.date_input('What range of dates are you interested in?', value=[])
    if range_dates:
        data_in_duration = get_data(database, range_dates)

        overall = st.sidebar.checkbox('See overall situtaion?')
        if overall:
            st.markdown('### IPQC interval during the selected period')
            barchart_of_whole_IPQC_time(data_in_duration)

            st.markdown('### Boxplot of (IPQC to measure finished) time')
            whole_data = data_of_whole_time(data_in_duration)
            boxplot_of_whole_time(whole_data)

            st.markdown('### Summary statistics of IPQC interval')
            st.dataframe(whole_data.describe().round(1))

        precision = st.sidebar.select_slider(
            'Which precision (D/W/M)?', ['Day', 'Week', 'Month'])

        if precision:
            detailed = st.sidebar.checkbox('Ready for detailed data?')
            if detailed:
                df_union, name_list = get_df_at_different_duration(
                    data_in_duration, precision[0])
                for i in range(len(df_union)):
                    st.markdown(name_list[i])
                    another_way_of_stack(df_union[i])

    else:
        st.info('Please give a time range or single date')
