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
        if "CNC_database" in file and '~$' not in file:  # 只处理该路径下的Excel文件
            pathss.append(root+file)

    data = pd.DataFrame()
    for file in pathss:
        df = pd.read_excel(file, index_col=[0])
        data = pd.concat([data, df])

    return data


def get_data(database, range_dates, FAI_point):
    time_format = '%Y-%m-%d'
    start_date = pd.to_datetime(str(range_dates[0]), format=time_format)
    end_date = pd.to_datetime(
        str(range_dates[1]), format=time_format) + pd.Timedelta(hours=23, minutes=59)

    # # extract the FAI data within the period
    mask = (database.index > start_date) & (database.index <= end_date)
    data_in_duration = database.loc[mask]
    # data_in_duration = data_in_duration.sort_index()
    data_in_duration = data_in_duration.set_index('Machine')

    return data_in_duration.loc[:, FAI_point]


def add_spec_v(FAI_config,  data):
    # to check whether it's series or dataframe
    #
    if data.name == 'FAI6':
        data.name = 'FAI6_A1'

    if len(data.shape) == 1:
        checked_data = FAI_config.loc[data.name]
        if checked_data[0]:
            plt.axvline(checked_data[0],
                        color='g', linestyle='dotted', linewidth=2.5, label='Nominal')
        if checked_data[1]:
            upper_limit = checked_data[0] + checked_data[1]
            plt.axvline(upper_limit,
                        color='r', linestyle='dotted', linewidth=2.5, label='TOL +')
        if checked_data[2]:
            lower_limit = checked_data[0] + checked_data[2]
            plt.axvline(lower_limit,
                        color='b', linestyle='dotted', linewidth=2.5, label='TOL --')
    else:
        number_of_FAI = len(data.columns)
        interval = 1/number_of_FAI

        for i in range(number_of_FAI):

            checked_data = FAI_config.loc[data.columns[i]]

            if checked_data[0]:
                plt.axvline(checked_data[0], i*interval, (i+1) * interval,
                            color='g', linestyle='dotted', label='Nominal')
            if checked_data[1]:
                upper_limit = checked_data[0] + checked_data[1]
                plt.axvline(upper_limit, i*interval, (i+1) * interval,
                            color='r', linestyle='dotted', label='TOL +')
            if checked_data[2]:
                lower_limit = checked_data[0] + checked_data[2]
                plt.axvline(lower_limit, i*interval, (i+1) * interval,
                            color='b', linestyle='dotted', label='TOL --')


def out_of_spec(s, FAI_number, FAI_config):
    upper = FAI_config.loc[FAI_number, 'upper']
    lower = FAI_config.loc[FAI_number, 'lower']

    if s > upper or s < lower:
        return 1
    else:
        return 0


def get_top_issue_CNC(data_no_T, FAI_config, FAI_point, n=None, frequency=None):

    if not n:
        n = 5

    if not frequency:
        n = 3

    top_issue_CNC = {}

    # prepare the CNC name
    index = [str(i)[:4] for i in data_no_T.index]
    data_no_T.index = index
    CNC_IPQC_frequency = data_no_T.index.value_counts()
    CNC_IPQC_frequency.name = 'Check_frequency'
    CNC_IPQC_frequency = CNC_IPQC_frequency.to_frame()

    result = data_no_T.apply(out_of_spec, args=(FAI_point, FAI_config,))

    NG_rate = [100 * result[index].sum()/CNC_IPQC_frequency.loc[index, 'Check_frequency']
               for index in CNC_IPQC_frequency.index]
    CNC_IPQC_frequency['NG_rate'] = NG_rate

    CNC_IPQC_frequency = CNC_IPQC_frequency[CNC_IPQC_frequency['Check_frequency'] >= frequency]
    CNC_IPQC_frequency = CNC_IPQC_frequency[CNC_IPQC_frequency['NG_rate'] > 0]

    if CNC_IPQC_frequency.empty:
        st.info('No CNC checked more than ' + str(frequency) + ' times')

    CNC_IPQC_frequency.sort_values('NG_rate', ascending=False, inplace=True)

    return CNC_IPQC_frequency.head(n)


def get_top_issue_FAI_plots(data_in_duration, top_issue_FAI, FAI_config):

    for FAI in top_issue_FAI.keys():
        filter_FAI = [col for col in data_in_duration if col.startswith(FAI)]
        data = data_in_duration[filter_FAI]

        if FAI == 'FAI6_':
            data = data.mean(axis=1)
            data.name = 'FAI6'
            data = data.to_frame()

        FAI_quantity = len(data.columns)
        if FAI_quantity <= 3:
            fig, ax = plt.subplots(1, FAI_quantity, figsize=(20, 10))
            st.text(FAI)
            for i in range(1, FAI_quantity + 1):
                plt.subplot(1, FAI_quantity, i)
                sns.histplot(x=data.iloc[:, i-1], color='gray', stat='density')
                sns.kdeplot(x=data.iloc[:, i-1], color='blue', linewidth=3)
                add_spec_v(FAI_config,  data.iloc[:, i-1])
            fig.tight_layout()
            st.pyplot(fig)
        elif FAI_quantity in range(4, 7):
            fig, ax = plt.subplots(2, ceil(FAI_quantity/2), figsize=(20, 10))
            st.text(FAI)
            for i in range(1, FAI_quantity + 1):
                plt.subplot(2, FAI_quantity//2, i)
                sns.histplot(x=data.iloc[:, i-1], color='gray', stat='density')
                sns.kdeplot(x=data.iloc[:, i-1], color='blue', linewidth=3)
                add_spec_v(FAI_config,  data.iloc[:, i-1])
            fig.tight_layout()
            st.pyplot(fig)
        else:
            fig, ax = plt.subplots(3, ceil(FAI_quantity/3), figsize=(20, 10))
            st.text(FAI)
            for i in range(1, FAI_quantity + 1):
                plt.subplot(3, ceil(FAI_quantity/3), i)
                sns.histplot(x=data.iloc[:, i-1], color='gray', stat='density')
                sns.kdeplot(x=data.iloc[:, i-1], color='blue', linewidth=3)
                add_spec_v(FAI_config,  data.iloc[:, i-1])
            fig.tight_layout()
            st.pyplot(fig)


def app():
    root = 'database/'
    database = get_database(root)
    FAI_config = pd.read_excel(root + 'FAI_config.xlsx', index_col='FAI#')
    FAI_config = FAI_config.iloc[:, 1:]

    # start of the streamlit
    # define the range of time
    range_dates = st.sidebar.date_input('What range of dates are you interested in?', value=[])
    FAI_point = st.sidebar.selectbox('Which FAI point?', database.columns[1:])
    if range_dates and FAI_point:  # once dates typed in
        data_in_duration = get_data(database, range_dates, FAI_point)

        n = st.sidebar.slider('How many top issues would like to see?', 3, 10)

        frequency = st.sidebar.slider('Lowest checking time?', 3, 10)

        CNC_IPQC_frequency = get_top_issue_CNC(
            data_in_duration, FAI_config, FAI_point, n, frequency)

        st.markdown('## Top issue CNC of ' + FAI_point + ' :')
        if not CNC_IPQC_frequency.empty:
            st.dataframe(CNC_IPQC_frequency)
            fig, ax = plt.subplots()
            ax = sns.barplot(x=CNC_IPQC_frequency.index, y='NG_rate',
                             data=CNC_IPQC_frequency)
            # ax.bar(CNC_IPQC_frequency.index, CNC_IPQC_frequency.NG_rate)
            st.pyplot(fig)
        else:
            st.markdown('# Not existed')

    else:
        st.info('Please give a time range or single date, and a specific FAI')
