import streamlit as st
import pandas as pd
from mlxtend.frequent_patterns import association_rules, apriori, fpgrowth
from mlxtend.preprocessing import TransactionEncoder
import streamlit_authenticator as stauth
import mysql.connector as mc
import pickle 
from pathlib import Path
from time import process_time
import database as db


st.set_page_config(page_title="Market Basket Analysis", page_icon="🧺️", layout="wide")

# Connect to Deta Base with your Data Key
#deta = Deta(st.secrets["data_key"])
#create/connect database
#db = deta.Base("db_mba")

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
    
    @st.cache_data(show_spinner="Mengambil data...")
    #preprocessing
    #load dataset csv
    def get_data_parque():
        df = pd.read_parquet("data_clean.parque", engine='auto')
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format="%Y-%m-%d %H:%M:%S")
        df["hour"] = df['InvoiceDate'].dt.hour
        df['hour'] = df['hour'].replace([6,7,8], "6 - 8")
        df['hour'] = df['hour'].replace([9,10,11], "9 - 11")
        df['hour'] = df['hour'].replace([12,13,14], "12 - 14")
        df['hour'] = df['hour'].replace([15,16,17], "15 - 17")
        df['hour'] = df['hour'].replace([18,19,20], "18 - 20")
        return df
    df = get_data_parque()

    
    # --- DATABASE INTERFACE ---
    def get_all_history():
        items = db.fetch_all_history()
        history = [item for item in items]
        return history
    def get_key():
        keys = db.fetch_all_history()
        key = [item["key"] for item in keys]
        return key

    def get_selected_keys(hd):
    # Dapatkan kunci yang dicentang dari dataframe
        selected_rows = hd[hd.Select]
        selected_keys = selected_rows["key"]  # Ubah "key" ke kolom yang sesuai dalam dataframe Anda
        return selected_keys

        #load dataset sql
    # @st.cache_data
    # def get_data_sql():
    #     mysqldb_conn = mc.connect(host="localhost", user="root", password="123", database="db_mba")
    #     sql_query = pd.read_sql_query("SELECT * FROM datacustomer_parque", mysqldb_conn)
    #     df = pd.DataFrame(sql_query)
    #     df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format="%Y-%m-%d %H:%M:%S")
    #     df["hour"] = df['InvoiceDate'].dt.hour
    #     df['hour'] = df['hour'].replace([6,7,8], "6 - 8")
    #     df['hour'] = df['hour'].replace([9,10,11], "9 - 11")
    #     df['hour'] = df['hour'].replace([12,13,14], "12 - 14")
    #     df['hour'] = df['hour'].replace([15,16,17], "15 - 17")
    #     df['hour'] = df['hour'].replace([18,19,20], "18 - 20")
    #     return df
    # df = get_data_sql()

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
            

            description = st.selectbox("Item name",
                df["Description"].unique()
            )
            df_selection= df.query(
                "Description == @description"
            )
            user_date_input = st.date_input(
                "Select the date",
                value=(df['InvoiceDate'].min(),
                df['InvoiceDate'].min()), min_value = min_date, max_value = max_date
            )
            
            if len(user_date_input) == 2:
                user_date_input = tuple(map(pd.to_datetime, user_date_input))
                start_date, end_date = user_date_input
                df_selection_by_datepicker = df.loc[df['InvoiceDate'].between(start_date, end_date)]
            else:
                st.warning("Harap pilih dua tanggal yang valid.")
            
                
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
            transactionEncoder = load_te()

            if type(df_selection_by_hour) != type(df_selection_by_hour):
                st.error("Tidak ada data" )
            
            if type(df_selection_by_hour) == type(df_selection_by_hour):
                
                #membuat market basket transactions
                dfgroup = df_selection_by_hour.groupby(['CustomerID','InvoiceDate'])['Description'].agg(lambda x: ','.join(x.dropna())).reset_index()
                dfgroup.sort_values(by='InvoiceDate', ascending=True, inplace=True,ignore_index=True)
                        
                dataset = []
                for i in range(len(dfgroup['Description'])):
                    new_val = dfgroup['Description'].iloc[i].split(',')
                    dataset.append(new_val)

            #Frequent itemsets generation
            te = transactionEncoder()
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
                data = rules[["antecedents", "consequents", "support", "confidence", "lift"]].copy()
                
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
                    st.markdown("Recommendation :" )
                    st.success(f"When customer buy **{description}**, then buy **{return_item_df(description)[1]}** at the same time")
            elif type(df_selection_by_hour) != type(df_selection_by_hour):
                st.error("Tidak ada data" )
            else:
                st.error("Index diluar jangkauan")


            t1_stop = process_time()
            st.info(f"Waktu analisis {t1_stop-t1_start} detik")

            antecedents = (f"{return_item_df(description)[0]}")
            consequents = f"{return_item_df(description)[1]}"
            support = f"{return_item_df(description)[2]:.3f}"
            confidence = f"{return_item_df(description)[3]:.3f}"
            lift = f"{return_item_df(description)[4]:.3f}"
            #key = f"{get_all_history()[0]}"
            
            submitted = st.button("Save Data", use_container_width=True)
            if submitted:
                db.insert_mba_history(antecedents, consequents, support, confidence, lift)
                st.success("Data saved!")

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


            # Mengambil data history
            history_data = get_all_history()

            # Konversi list ke DataFrame
            hd = pd.DataFrame(history_data, columns=["antecedents", "consequents", "support", "confidence", "lift", "key"])

            def dataframe_with_selections(hd):
                #hd_with_selections = hd.copy()
                hd.insert(0, "Select", False)

            # Get dataframe row-selections from user with st.data_editor
                edited_hd = st.data_editor(
                    hd,
                    hide_index=True,
                    column_config={"Select": st.column_config.CheckboxColumn(required=True)},
                    disabled=["antecedents", "consequents", "support", "confidence", "lift", "key"],
                )
                tambah = st.button('Delete', key='Select', type="primary", use_container_width=True)
                #keys = get_key()
                if tambah:
                    selected_keys = get_selected_keys(edited_hd)
                # Filter the dataframe using the temporary column, then drop the column
                    for key in selected_keys:
                    # selected_rows = edited_hd[edited_hd.Select]
                    #if not selected_rows.empty:
                        db.delete_history(key)
                        return selected_keys.drop(edited_hd.Select)
                        st.success("Data deleted!")
                    

                # Menampilkan DataFrame dengan kolom "Delete"
            #st.dataframe(hd)
            st.header("Association Table")
            def showTable():
                dfgroup = df_selection_by_hour.groupby(['CustomerID','InvoiceDate'])['Description'].agg(lambda x: ','.join(x.dropna())).reset_index()
                dfgroup.sort_values(by='InvoiceDate', ascending=True, inplace=True,ignore_index=True)

                dataset = []
                for i in range(len(dfgroup['Description'])):
                    new_val = dfgroup['Description'].iloc[i].split(',')
                    dataset.append(new_val)

                te = transactionEncoder()
                te_ary = te.fit(dataset).transform(dataset,sparse=True)
                df_new = pd.DataFrame.sparse.from_spmatrix(te_ary, columns=te.columns_)
                frequent_items = model(df_new, min_support=0.02, use_colnames=True)
                rules = associationRules(frequent_items, metric="lift", min_threshold=1)[["antecedents", "consequents", "support", "confidence", "lift"]]
                
                rules['antecedents'] = rules['antecedents'].apply(list)
                rules['consequents'] = rules['consequents'].apply(list)
                
                # rules1 = rules1.drop(224)
                # rules1 = rules1.drop(225)
                # rules = rules1[(rules1['lift'] >= 1)&
                # (rules1['confidence'] <= 1)]
                # rules = rules[rules['antecedents'].apply(lambda x: len(x) > 0)]
                #rules.sort_values('confidence', ascending=False, inplace=True)
                
                    # rules = association_rules(frequent_items_fp, metric="confidence", min_threshold=0.05)

                    # rules = association_rules(frequent_items_fp, metric="lift", min_threshold=1)[["antecedents", "consequents", "support", "confidence", "lift"]]
                    # rules.sort_values('confidence', ascending=False, inplace=True)
                return rules
            st.dataframe(showTable(), use_container_width=True)
            st.markdown("---")

            st.header("Saved Data")
            selection = dataframe_with_selections(hd)
            # st.write("Your selection:")
            # st.write(selection)
        
        else:
            st.warning("Masukkan data lengkap")
        st.write(get_all_history())
        
        


        # --- HIDE STREAMLIT STYLE ---
# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)

        

        
        



