#from backup_fpgrowth import get_data
from re import L
from altair.vegalite.v5.schema.channels import Column
from mlxtend import frequent_patterns
from mysql.connector.fabric import connect
from pandas.core import algorithms
from pandas.core.indexes.base import Index
from sqlalchemy import create_engine
import streamlit as st
import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import association_rules, apriori, fpgrowth
from mlxtend.preprocessing import TransactionEncoder
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth
import mysql.connector as mc
import sqlite3
import pickle 
from pathlib import Path
import datetime
from time import process_time

from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st.set_page_config(page_title="Market Basket Analysis", page_icon="🧺️", layout="wide")


# ----USER-AUTH
names = ["Admin 1", "Admin 2"]
usernames = ["admin1", "admin2"]
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

credentials = {
        "usernames":{
            usernames[0]:{
                "name":names[0],
                "password":hashed_passwords[0]
                },
            usernames[1]:{
                "name":names[1],
                "password":hashed_passwords[1]
                }            
            }
        }

authenticator = stauth.Authenticate(credentials, "mba_dashboard", "abcdef", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")


if authentication_status:
    # st.success("Berhasil")
    st.sidebar.title(f"Welcome {name}")
    #convert sql to dataframe
    #dfsql = pd.DataFrame(sql_query, columns = ['InvoiceNo', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country'])
    #print(dfsql)
    authenticator.logout("Logout", "sidebar")
    
    #@st.cache_data(show_spinner="Mengambil data...")
    #preprocessing
    #load dataset csv
    # def get_data_parque():
    #     df = pd.read_parquet("data_clean.parque", engine='auto')
    #     df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format="%Y-%m-%d %H:%M:%S")
    #     df["hour"] = df['InvoiceDate'].dt.hour
    #     df['hour'] = df['hour'].replace([6,7,8], "6 - 8")
    #     df['hour'] = df['hour'].replace([9,10,11], "9 - 11")
    #     df['hour'] = df['hour'].replace([12,13,14], "12 - 14")
    #     df['hour'] = df['hour'].replace([15,16,17], "15 - 17")
    #     df['hour'] = df['hour'].replace([18,19,20], "18 - 20")
    #     return df
    # df = get_data_parque()

    

        #load dataset sql
    @st.cache_data
    def get_data_sql():
        mysqldb_conn = mc.connect(host="localhost", user="root", password="123", database="db_mba")
        sql_query = pd.read_sql_query("SELECT * FROM datacustomer_parque", mysqldb_conn)
        df = pd.DataFrame(sql_query)
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format="%Y-%m-%d %H:%M:%S")
        df["hour"] = df['InvoiceDate'].dt.hour
        df['hour'] = df['hour'].replace([6,7,8], "6 - 8")
        df['hour'] = df['hour'].replace([9,10,11], "9 - 11")
        df['hour'] = df['hour'].replace([12,13,14], "12 - 14")
        df['hour'] = df['hour'].replace([15,16,17], "15 - 17")
        df['hour'] = df['hour'].replace([18,19,20], "18 - 20")
        return df
    df = get_data_sql()

    with st.sidebar:
        # st.header("ini header")
        # st.button("tombol")
        algo = st.radio(
            "Choose algorithm",
            ['FPGrowth','Apriori']
        )
    if algo == 'Apriori':
        st.title("Market Basket Analysis Menggunakan Algoritma Apriori")    

    else:

        st.title("Market Basket Analysis Menggunakan Algoritma FPGrowth")    

        def filterDashboard(df: pd.DataFrame):
            min_date = df['InvoiceDate'].min()
            max_date = df['InvoiceDate'].max()
            df_selection_by_datepicker = pd.DataFrame()

            description = st.selectbox("Item",
                df["Description"].unique()
            )
            df_selection= df.query(
                "Description == @description"
            )
            user_date_input = st.date_input(
                f"Values for {'InvoiceDate'}",
                value=(df['InvoiceDate'].min(),
                df['InvoiceDate'].min()), min_value = min_date, max_value = max_date
            )
            if len(user_date_input) == 2:
                user_date_input = tuple(map(pd.to_datetime, user_date_input))
                start_date, end_date = user_date_input
                df_selection_by_datepicker = df.loc[df['InvoiceDate'].between(start_date, end_date)]

            hour = st.multiselect(
                "Select the hour:",
                options=df_selection_by_datepicker["hour"].sort_values().unique(),
                default=df_selection_by_datepicker["hour"].unique()
            )        
            df_selection_by_hour = df_selection_by_datepicker.query(
                "hour == @hour"
            )
          
            
            return description, df_selection_by_datepicker,df_selection_by_hour
        description, df_selection_by_datepicker, df_selection_by_hour = filterDashboard(df)

        if df_selection_by_hour.empty is False:
        # def get_data(hour = ''):
        #     data = df_selection.copy()
        #     data["hour"] = data["hour"].astype(str)
        #     filtered = data.loc[
        #         (data["hour"].str.contains(str(hour)))
                
        #     ]
        #     return filtered if filtered.shape[0] else "No Result!"

        #data = get_data(df_selection)

        
            t1_start = process_time()
            def encode(x):
                if x <= 0:
                    return 0
                elif x >= 1 :
                    return 1
            
            @st.cache_data
            def load_model():
                return fpgrowth
            model = load_model()

            @st.cache_data
            def load_rules():
                return association_rules
            associationRules = load_rules()

            @st.cache_data
            def load_te():
                return TransactionEncoder
            transactionencoder = load_te()

            if type(df_selection_by_hour) != type(df_selection_by_hour):
                st.error("Tidak ada data" )
            
            if type(df_selection_by_hour) == type(df_selection_by_hour):
                # REDFLAG LAMA PARAH 48dtk vs 9dtk
                # item_count = df.groupby(["InvoiceNo", "Description"])["Description"].count().reset_index(name = "Count")
                # item_count_pivot = item_count.pivot_table(index='InvoiceNo', columns='Description', values='Count', aggfunc='sum').fillna(0)
                # item_count_pivot = item_count_pivot.map(encode)
                #     #pemanggilan fpgrowth
                # support = 0.02
                # frequent_items = model(item_count_pivot, min_support=support, use_colnames=True)
                # metric = "lift"
                # min_threshold = 1
                # rules = associationRules(frequent_items, metric=metric, min_threshold=min_threshold)[["antecedents", "consequents", "support", "confidence", "lift"]]
                # rules.sort_values('confidence', ascending=False, inplace=True)
                #rules = rules.drop(224)
                #rules = rules.drop(225)
                
                #membuat market basket transactions
                dfgroup = df_selection_by_hour.groupby(['CustomerID','InvoiceDate'])['Description'].agg(lambda x: ','.join(x.dropna())).reset_index()
                dfgroup.sort_values(by='InvoiceDate', ascending=True, inplace=True,ignore_index=True)
                        
                dataset = []
                for i in range(len(dfgroup['Description'])):
                    new_val = dfgroup['Description'].iloc[i].split(',')
                    dataset.append(new_val)

            #Frequent itemsets generation
            te = transactionencoder()
            te_ary = te.fit(dataset).transform(dataset,sparse=True)
            df_new = pd.DataFrame.sparse.from_spmatrix(te_ary, columns=te.columns_)
            frequent_items = model(df_new, min_support=0.02, use_colnames=True)
            rules = associationRules(frequent_items, metric="lift", min_threshold=1)[["antecedents", "consequents", "support", "confidence", "lift"]]
            # rules = association_rules(frequent_items, metric="confidence", min_threshold=0.5)[["antecedents", "consequents", "support", "confidence", "lift"]]

            #st.cache_data(ttl=24*60*60, show_spinner="Mengambil data...")
            def parse_list(x):
                x = list(x)
                if len(x) == 1:
                    return x[0]
                elif len(x) > 1:
                    return ", ".join(x)
            #st.cache_data(ttl=24*60*60, show_spinner="Mengambil data...")
            def return_item_df(item_antecedents):
                data = rules[["antecedents", "consequents"]].copy()
                
                data["antecedents"] = data["antecedents"].apply(parse_list)
                data["consequents"] = data["consequents"].apply(parse_list)

                filtered_data = list(data.loc[data["antecedents"] == item_antecedents].iloc[0,:])              
                # if len(filtered_data) < 0:
                #     str.warning("Tidak ada data yang valid yang cocok dengan item_antecedents.")
                return filtered_data
                    
                 
            if type(df_selection_by_hour) == type(df_selection_by_hour):
                if return_item_df(description)[0] != description:
                    st.warning("Tidak ada data yang valid yang cocok dengan item_antecedents.")
                else:
                    st.markdown("Hasil Rekomendasi :" )
                    st.success(f"Ketika pelanggan membeli **{description}**, maka membeli **{return_item_df(description)[1]}** secara bersamaan")
            elif type(df_selection_by_hour) != type(df_selection_by_hour):
                st.error("Tidak ada data" )
            else:
                st.error("Index diluar jangkauan")

            
            def showKPI():
                total_sales = int((df_selection_by_hour["UnitPrice"]*df_selection_by_hour["Quantity"]).sum())
                average_sale_by_transaction = round((df_selection_by_hour["UnitPrice"]*df_selection_by_hour["Quantity"]).mean(), 2)
                left_column, right_column = st.columns(2)
                with left_column:
                    st.subheader("Sales total:")
                    st.subheader(f"US $ {total_sales:,}")
                with right_column:
                    st.subheader("Average sales by transaction:")
                    st.subheader(f"US $ {average_sale_by_transaction}")
                st.markdown("---")
                print("Sales count :", total_sales)
            showKPI()

            t1_stop = process_time()
            st.info(f"Waktu analisis {t1_stop-t1_start} detik")

        else:
            st.warning("Masukkan data lengkap")
        
        # @st.cache_data
        # def showTable():
        #     #dataasli = pd.read_csv("data_clean.csv", encoding='latin-1')
        #     dataasli_group = df_selection_by_hour.groupby(['CustomerID','InvoiceDate'])['Description'].agg(lambda x: ','.join(x.dropna())).reset_index()
        #     dataasli_group.sort_values(by='InvoiceDate', ascending=True, inplace=True,ignore_index=True)
        #     #dataasli_group

        #     dataset = []
        #     for i in range(len(dataasli_group['Description'])):
        #         new_val = dataasli_group['Description'].iloc[i].split(',')
        #         dataset.append(new_val)

        #     te = TransactionEncoder()
        #     te_ary = te.fit(dataset).transform(dataset)
        #     df_new = pd.DataFrame(te_ary, columns=te.columns_)

        #     frequent_items_fp = fpgrowth(df_new, min_support=0.02, use_colnames=True)
        #     #frequent_items_fp

        #     rules1 = association_rules(frequent_items_fp, metric="lift", min_threshold=1)[["antecedents", "consequents", "support", "confidence", "lift"]]
            
        #     rules1['antecedents'] = rules1['antecedents'].apply(list)
        #     rules1['consequents'] = rules1['consequents'].apply(list)
            
        #     # rules1 = rules1.drop(224)
        #     # rules1 = rules1.drop(225)
        #     # rules = rules1[(rules1['lift'] >= 1)&
        #     # (rules1['confidence'] <= 1)]
        #     # rules = rules[rules['antecedents'].apply(lambda x: len(x) > 0)]
        #     #rules.sort_values('confidence', ascending=False, inplace=True)
            
        #         # rules = association_rules(frequent_items_fp, metric="confidence", min_threshold=0.05)

        #         # rules = association_rules(frequent_items_fp, metric="lift", min_threshold=1)[["antecedents", "consequents", "support", "confidence", "lift"]]
        #         # rules.sort_values('confidence', ascending=False, inplace=True)
        #     return rules1
        # st.dataframe(showTable(), use_container_width=True)
        st.write("dataframe rules : ")
        rules

        # def filter_dataframe(df: pd.DataFrame, key_name: str) -> pd.DataFrame:
        #     rules['antecedents'] = rules['antecedents'].apply(list)
        #     rules['consequents'] = rules['consequents'].apply(list)
        #     modify = st.checkbox("Add filters", key=f"{key_name}")
        #     if not modify:
        #         return df
        #     df = df.copy()
        #     for col in df.columns:
        #         if is_object_dtype(df[col]):
        #             try:
        #                 df[col] = pd.to_datetime(df[col])
        #             except Exception:
        #                 pass
        #         if is_datetime64_any_dtype(df[col]):
        #             df[col] = df[col].dt.tz_localize(None)
        #     modification_container = st.container()
        #     with modification_container:
        #         to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        #         for column in to_filter_columns:
        #             left, right = st.columns((1, 20))
        #             # if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
        #             #     user_cat_input = right.multiselect(f"Values for {column}",df[column].unique(),default=list(df[column].unique()),)
        #             #     df = df[df[column].isin(user_cat_input)]
        #             if is_numeric_dtype(df[column]):
        #                 _min = float(df[column].min())
        #                 _max = float(df[column].max())
        #                 step = (_max - _min) / 100
        #                 user_num_input = right.slider(f"Values for {column}",min_value=_min,max_value=_max,value=(_min, _max),step=step,)
        #                 df = df[df[column].between(*user_num_input)]
        #             elif is_datetime64_any_dtype(df[column]):
        #                 user_date_input = right.date_input(f"Values for {column}",value=(df[column].min(),df[column].max(),),)
        #                 if len(user_date_input) == 2:
        #                     user_date_input = tuple(map(pd.to_datetime, user_date_input))
        #                     start_date, end_date = user_date_input
        #                     df = df.loc[df[column].between(start_date, end_date)]
        #             # else:
        #             #     user_text_input = right.text_input(f"Substring or regex in {column}",)
        #             #     if user_text_input:
        #             #         df = df[df[column].astype(str).str.contains(user_text_input)]
        #     return df   
        # st.dataframe(filter_dataframe(rules, "mba"), use_container_width=True)
        # st.write("tanggal maksimal : ", df['InvoiceDate'].max())
        
        # st.write("tanggal minimal : ", df['InvoiceDate'].min())
        # st.write("dataframe df_selection : ")
        # df_selection

        # st.write("dataframe df_selection_by_hour : ")
        # if type(df_selection_by_hour) == type(df_selection_by_hour):
        #     df_selection_by_hour
        

        
        



