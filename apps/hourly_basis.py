import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import itertools
# add 图纸sepcs other than IPQC specs
# by machine to check FAI
# Used functions


def app():

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

    def add_spec_h(FAI_config,  data):
        # to check whether it's series or dataframe
        if len(data.shape) == 1:
            checked_data = FAI_config.loc[data.name]
            if checked_data[0]:
                plt.axhline(checked_data[0],
                            color='g', linestyle='dotted', linewidth=2.5, label='Nominal')
            if checked_data[1]:
                upper_limit = checked_data[0] + checked_data[1]
                plt.axhline(upper_limit,
                            color='r', linestyle='dotted', linewidth=2.5, label='TOL +')
            if checked_data[2]:
                lower_limit = checked_data[0] + checked_data[2]
                plt.axhline(lower_limit,
                            color='b', linestyle='dotted', linewidth=2.5, label='TOL --')
        else:
            number_of_FAI = len(data.columns)
            interval = 1/number_of_FAI

            for i in range(number_of_FAI):

                checked_data = FAI_config.loc[data.columns[i]]

                if checked_data[0]:
                    plt.axhline(checked_data[0], i*interval, (i+1) * interval,
                                color='g', linestyle='dotted', label='Nominal')
                if checked_data[1]:
                    upper_limit = checked_data[0] + checked_data[1]
                    plt.axhline(upper_limit, i*interval, (i+1) * interval,
                                color='r', linestyle='dotted', label='TOL +')
                if checked_data[2]:
                    lower_limit = checked_data[0] + checked_data[2]
                    plt.axhline(lower_limit, i*interval, (i+1) * interval,
                                color='b', linestyle='dotted', label='TOL --')

    def add_spec_v(FAI_config,  data):
        # to check whether it's series or dataframe
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

    def get_df_at_different_points_duration(data, precision):
        length = data.shape[1]
        df_union = [pd.DataFrame() for i in range(length)]
        # df_single = pd.DataFrame()
        name_list = []
        if length == 1:
            for name, df in data.resample(precision):
                df.dropna(how='all', inplace=True)
                if len(df.index):
                    name_list.append(name)
                    df.reset_index(inplace=True, drop=True)
                    df_union[0] = pd.concat([df_union[0], df], axis=1)
            df_union[0].columns = name_list
        else:
            for name, df in data.resample(precision):
                df.dropna(how='all', inplace=True)
                if len(df.index):
                    name_list.append(name)
                    df.reset_index(inplace=True, drop=True)
                    for i in range(length):
                        df_union[i] = pd.concat([df_union[i], df.iloc[:, i]], axis=1)
            for df in df_union:
                df.columns = name_list

        return df_union, length

    def plot_different_points_duration(df_union, filter_FAI, FAI_config, length, mode):
        if mode == 'box':
            for i in range(length):
                fig, ax = plt.subplots()
                fig = plt.figure(figsize=(10, 5))
                FAI_number = filter_FAI[i]
                ax = sns.boxplot(data=df_union[i])
                ax = sns.swarmplot(data=df_union[i], color=".5", size=4.5)
                # ax = sns.catplot(kind=mode,  data=df_union[i]).set(title=FAI_number)
                # ax.fig.set_size_inches(10, 5)
                ax.set_xticklabels(labels=df_union[i].columns, rotation=30)
                ax.set_title(FAI_number)

                checked_data = FAI_config.loc[FAI_number]

                if checked_data[0]:
                    plt.axhline(checked_data[0],
                                color='g', linestyle='dotted', linewidth=2.5, label='Nominal')
                if checked_data[1]:
                    upper_limit = checked_data[0] + checked_data[1]
                    plt.axhline(upper_limit,
                                color='r', linestyle='dotted', linewidth=2.5, label='TOL +')
                if checked_data[2]:
                    lower_limit = checked_data[0] + checked_data[2]
                    plt.axhline(lower_limit,
                                color='b', linestyle='dotted', linewidth=2.5, label='TOL --')
                st.pyplot(fig)
        else:
            for i in range(length):
                fig, ax = plt.subplots()
                fig = plt.figure(figsize=(10, 5))
                FAI_number = filter_FAI[i]
                ax = sns.violinplot(data=df_union[i])
                ax = sns.swarmplot(data=df_union[i], color='white', size=5)
                # ax = sns.catplot(kind=mode,  data=df_union[i]).set(title=FAI_number)
                # ax.fig.set_size_inches(10, 5)
                ax.set_xticklabels(labels=df_union[i].columns, rotation=30)
                ax.set_title(FAI_number)

                checked_data = FAI_config.loc[FAI_number]

                if checked_data[0]:
                    plt.axhline(checked_data[0],
                                color='g', linestyle='dotted', linewidth=2.5, label='Nominal')
                if checked_data[1]:
                    upper_limit = checked_data[0] + checked_data[1]
                    plt.axhline(upper_limit,
                                color='r', linestyle='dotted', linewidth=2.5, label='TOL +')
                if checked_data[2]:
                    lower_limit = checked_data[0] + checked_data[2]
                    plt.axhline(lower_limit,
                                color='b', linestyle='dotted', linewidth=2.5, label='TOL --')
                st.pyplot(fig)

    def plot_different_points_kde_duration(df_union, filter_FAI, FAI_config, length):
        for i in range(length):
            FAI_number = filter_FAI[i]
            fig, ax = plt.subplots(figsize=(10, 5))
        #     ax = sns.catplot(kind='box', data=df_union[i]).set(title=FAI_number)
            palette = itertools.cycle(sns.color_palette())
            for column in df_union[i].columns:
                sns.kdeplot(ax=ax, x=df_union[i].loc[:, column],
                            linewidth=3, label=column, color=next(palette), shade=True).set(title=FAI_number)
        #     ax.fig.set_size_inches(10, 5)
        #     ax.set_xticklabels(rotation=30)

            checked_data = FAI_config.loc[FAI_number]
            plt.xlabel(" ")
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)

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

            st.pyplot(fig)

    # Initiaion
    root = 'database/'
    database = get_database(root)
    cnc_cell = pd.read_excel(root + 'CNC_cell.xlsx')
    FAI_config = pd.read_excel(root + 'FAI_config.xlsx', index_col='FAI#')
    FAI_config = FAI_config.iloc[:, 1:]
    # start of the streamlit
    # define the range of time
    range_dates = st.sidebar.date_input('What range of dates are you interested in?', value=[])
    time_format = '%Y-%m-%d'
    if range_dates:
        start_date = pd.to_datetime(str(range_dates[0]), format=time_format)
        end_date = pd.to_datetime(
            str(range_dates[1]), format=time_format) + pd.Timedelta(hours=23, minutes=59)
    # extract the FAI data within the period
        mask = (database.index > start_date) & (database.index <= end_date)
        data_in_duration = database.loc[mask].sort_index()
    else:
        st.info('Please specify the time range or a single date')
    by_cell = st.sidebar.checkbox('By CNC cell?')
    if by_cell:
        cell_number = st.sidebar.multiselect('Select the CNC cell', cnc_cell.columns)
        data_by_cell = pd.DataFrame()
        if cell_number:
            data_in_duration['Machine'] = [i[:4] for i in data_in_duration['Machine']]
            data_by_cell = pd.DataFrame()
            for cell in cell_number:
                mask_cell = data_in_duration['Machine'].isin(cnc_cell[cell])
                data_in_duration = data_in_duration[mask_cell]
                data_by_cell = pd.concat([data_by_cell, data_in_duration])

            data_in_duration = data_by_cell

        # st.dataframe(data_in_duration)

    point_or_customization = st.sidebar.select_slider(
        'Fixed FAIs or preferred?', ['Fixed', 'Preference'])
    if point_or_customization:
        if point_or_customization == 'Fixed':
            number = st.sidebar.text_input('FAI #?')
            if number:
                FAI_number = 'FAI' + number + '_'
                filter_FAI = [col for col in data_in_duration if col.startswith(FAI_number)]
                if filter_FAI:
                    data = data_in_duration[filter_FAI]
                    violin_or_box = st.sidebar.select_slider('Box/Violin', ['box', 'violin'])
                    if violin_or_box:
                        st.markdown('### ' + violin_or_box.capitalize() +
                                    'plot over the duration selected')
                        fig, ax = plt.subplots()
                        g = sns.catplot(kind=violin_or_box, data=data)
                        # g = sns.stripplot(data=data, color="orange", jitter=0.2, size=2.5)
                        g.fig.set_size_inches(10, 5)
                        g.set_xticklabels(rotation=40)
                        add_spec_h(FAI_config,  data)
                        st.pyplot(g)

                else:
                    st.info('Please specify FAIs')
        else:
            filter_FAI = st.sidebar.multiselect(
                'Which FAIs?', options=FAI_config.index, help='Select at least 2 FAIs')
            if filter_FAI:
                data = data_in_duration[filter_FAI]
                violin_or_box = st.sidebar.select_slider('Box/Violin', ['box', 'violin'])
                if violin_or_box:
                    st.markdown('### ' + violin_or_box.capitalize() +
                                'plot over the duration selected')
                    fig, ax = plt.subplots()
                    g = sns.catplot(kind=violin_or_box, data=data)
                    # g = sns.stripplot(data=data, color="orange", jitter=0.2, size=2.5)
                    g.fig.set_size_inches(10, 5)
                    g.set_xticklabels(rotation=40)
                    add_spec_h(FAI_config,  data)
                    st.pyplot(g)

        review_by_day = st.sidebar.checkbox('Review by H/D/W/M?')
        if review_by_day:
            # st.sidebar.markdown('## Review by H/D/W/M')

            precision = st.sidebar.select_slider(
                'Which precision?', ['Hour', 'Day', 'Week', 'Month'])
            mode = st.sidebar.select_slider(
                'Box/Violin/Density?', ['box', 'violin', 'Density'])
            # st.dataframe(data)
            # st.write(data.shape[1])
            df_union, length = get_df_at_different_points_duration(data, precision[0])
            ready = st.sidebar.checkbox('Ready?')
            if ready:
                if (mode == 'box') | (mode == 'violin'):
                    st.markdown('### ' + mode +
                                'plot of the FAI selected by ' + precision)
                    plot_different_points_duration(
                        df_union, filter_FAI, FAI_config, length, mode)
                else:
                    st.markdown('### ' + 'KDE' +
                                'plot of the FAI selected by ' + precision)
                    plot_different_points_kde_duration(
                        df_union, filter_FAI, FAI_config, length)
