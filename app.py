import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import streamlit as st
import plotly.express as px


engine = create_engine('mysql+mysqlconnector://root:pwd123@127.0.0.1/phonepe_pulse')

aggregated_transaction_df = pd.read_sql_table("aggregated_transaction",con=engine)
aggregated_user_df = pd.read_sql_table("aggregated_user",con=engine)
map_transaction_df = pd.read_sql_table("map_transaction",con=engine)
map_user_df = pd.read_sql_table("map_user",con=engine)
top_transaction_dist_df = pd.read_sql_table("top_transaction_dist",con=engine)
top_transaction_pincode_df = pd.read_sql_table("top_transaction_pincode",con=engine)
top_user_dist_df = pd.read_sql_table("top_user_dist",con=engine)
top_user_pincode_df = pd.read_sql_table("top_user_pincode",con=engine)


aggregated_transaction_df['avg_amount'] = (aggregated_transaction_df['amount'] / aggregated_transaction_df['count_transaction']).astype(int)

map_transaction_df['avg_amount'] = (map_transaction_df['amount_map']/ map_transaction_df['count_map']).astype(int)

top_transaction_dist_df['avg_amount'] = (top_transaction_dist_df['amount_top']/top_transaction_dist_df['count_top']).astype(int)

top_transaction_pincode_df['avg_amount'] = (top_transaction_pincode_df['amount_top']/top_transaction_pincode_df['count_top']).astype(int)

st.title("Phonepe Pulse Data Visualization") # project title

with st.sidebar:
    st.header("Payments")

transaction_parts = ['Transaction','Users']
Payments = st.sidebar.selectbox('Payments',transaction_parts)

years = aggregated_transaction_df['year'].unique()
quarter_agg = aggregated_transaction_df['quarter'].unique()
categories = aggregated_transaction_df['name'].unique()
state = map_transaction_df['state'].unique() 

selected_year = st.sidebar.selectbox('Select year',sorted(years))
selected_quarter = st.sidebar.selectbox('Select quarter',sorted(quarter_agg))

if Payments == 'Transaction':
    aggregated_transaction_sum =aggregated_transaction_df.groupby(by='year').sum().reset_index()
    aggregated_transaction_sum["avg_amount"] = (aggregated_transaction_sum['amount'] / aggregated_transaction_sum['count_transaction']).astype(int)

    fig_bar_aggregated_transaction_sum = px.bar(
        aggregated_transaction_sum,
        x = 'year',
        y = 'amount',
        color='count_transaction',
        text_auto='.2s',
        color_continuous_scale="Portland",
        title="Total Transacation value over the years"
        )
    fig_bar_aggregated_transaction_sum.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)

    st.plotly_chart(fig_bar_aggregated_transaction_sum)


    aggregated_transaction_df2 = aggregated_transaction_df[(aggregated_transaction_df['year'] == selected_year) & (aggregated_transaction_df['quarter'] == selected_quarter) ]

    st.subheader(f'Categories and Transaction value for_{selected_quarter}_{selected_year}')

    aggregated_transaction_df3 = aggregated_transaction_df2.groupby(['name']).sum().reset_index()
    aggregated_transaction_df3.drop(['year','quarter','count_transaction','state','avg_amount'],axis=1,inplace=True)
    aggregated_transaction_df4 = aggregated_transaction_df3[['name','amount']].sort_values(by='amount',ascending=False).reset_index(drop=True)
    st.dataframe(aggregated_transaction_df4)

    tab1, tab2 = st.tabs(["Categories by Selection", "all Categories"])


    selected_categories =  tab1.selectbox("categories", categories)

    aggregated_transaction_df1 = aggregated_transaction_df[(aggregated_transaction_df['year'] == selected_year) & (aggregated_transaction_df['quarter'] == selected_quarter) & (aggregated_transaction_df['name'] == selected_categories) ]

    categories_agg = aggregated_transaction_df1.sort_values(by='amount',ascending=False).head(10).reset_index(drop=True)

    fig = px.choropleth(
        aggregated_transaction_df1,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='state',
        hover_name = 'state',
        hover_data = ['avg_amount'],        
        color='amount',
        color_continuous_scale="Portland",
        title=f'{selected_categories}_{selected_quarter}_{selected_year}'
    )
    fig.update_geos(fitbounds="locations", visible=False)

    tab1.plotly_chart(fig)


    fig_bar = px.bar(
        categories_agg,
        x = 'state',
        y = 'amount',
        color='avg_amount',
        text_auto='.2s',
        color_continuous_scale="Portland",
        title=f'{selected_quarter}_{selected_year}_Top 10 States in {selected_categories} by Transacation_Amount'
        )
    fig_bar.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    tab1.plotly_chart(fig_bar)

    for n in categories:
        aggregated_transaction_df1 = aggregated_transaction_df[(aggregated_transaction_df['year'] == selected_year) & (aggregated_transaction_df['quarter'] == selected_quarter) & (aggregated_transaction_df['name'] == n) ]

        fig = px.choropleth(
            aggregated_transaction_df1,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',
            locations='state',
            hover_name = 'state',
            hover_data = ['avg_amount'],        
            color='amount',
            color_continuous_scale="Portland",
            title=f'{n}_{selected_quarter}_{selected_year}'
        )
        fig.update_geos(fitbounds="locations", visible=False)

        tab2.plotly_chart(fig)

    for n in categories:

        fig_bar = px.bar(
            categories_agg,
            x = 'state',
            y = 'amount',
            color='avg_amount',
            text_auto='.2s',
            color_continuous_scale="Portland",
            title=f'{selected_quarter}_{selected_year}_Top 10 States in {n} by Transacation_Amount'
            )
        fig_bar.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        tab2.plotly_chart(fig_bar)


    fig_agg_pie= px.pie(
        aggregated_transaction_df2,
        values='amount',
        names='name',
        title=f'Categories_{selected_quarter}_{selected_year}',
        hover_data = ['avg_amount'] )
    fig_agg_pie.update_traces(textposition='inside', textinfo='percent+label')

    st.plotly_chart(fig_agg_pie)    


    map_transaction_df1 = map_transaction_df[(map_transaction_df['year']==selected_year) & (map_transaction_df['quarter']==selected_quarter)].reset_index(drop=True)
    

    map_transaction_df2 = map_transaction_df1.groupby(['state']).sum().reset_index()
    map_transaction_df3 = map_transaction_df2.drop(['year','quarter','dist_name','avg_amount'],axis=1)
    map_transaction_df3['avg_amount'] = (map_transaction_df3['amount_map'] / map_transaction_df3['count_map']).astype(int)
    map_transaction_df4 = map_transaction_df3.drop(['count_map'],axis=1)
    map_transaction_df5 = map_transaction_df4.sort_values(by = 'amount_map',ascending=False).reset_index(drop=True).head(10)
    map_transaction_df5.index = map_transaction_df5.index + 1
    map_transaction_df5.index = map_transaction_df5.index.rename("Sl.No")

    map_transaction_df4.index = map_transaction_df4.index + 1
    map_transaction_df4.index = map_transaction_df4.index.rename("Sl.No")
    
    map_amount_sum = int(map_transaction_df4['amount_map'].sum())
    map_total_transaction = map_transaction_df3['amount_map'].sum()
    map_total_transaction_count = map_transaction_df3['count_map'].sum()
    map_avg_amount= int(map_total_transaction/ map_total_transaction_count)

    st.subheader(f"{selected_year}_{selected_quarter} Transaction summary")
    st.write(f"Total Transaction = **₹{map_total_transaction:,}**")
    st.write(f"Total Transaction count = **{map_total_transaction_count:,}**")
    st.write(f"Average amount per Transaction = **₹{map_avg_amount }**")
    st.subheader(f'Top 10 States in {selected_year}_{selected_quarter}')
    st.dataframe(map_transaction_df5,use_container_width=True)

    fig_map = px.choropleth(
        map_transaction_df1,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='state',
        hover_name = 'state',
        hover_data = ['avg_amount','amount_map'],        
        color='count_map',
        color_continuous_scale="Portland",
        title=f"{selected_year}_{selected_quarter} Transaction history for each state"
        )
    fig_map.update_geos(fitbounds="locations", visible=False)

    st.plotly_chart(fig_map)
    st.dataframe(map_transaction_df4,use_container_width=True)

    fig_map_transacation = px.treemap(
        map_transaction_df1 , 
        path = ['state','dist_name'], 
        values='amount_map',
        color='amount_map',
        color_continuous_scale="Greens",
        title=f"{selected_year}_{selected_quarter} Transaction summary for each state"
        )
    fig_map_transacation.update_traces(textinfo='label+value+percent parent')
    st.plotly_chart(fig_map_transacation,use_container_width=True) 

    st.subheader(f"{selected_year}_{selected_quarter} Top Transaction by Districts and pincode's for each state")

    tab1, tab3 = st.tabs(["Top District in Each State by selection","Top District in Each State"])
    tab2, tab4 = st.tabs(["Top Pincode's in Each State by selection","Top Pincode's in Each State"])


    selected_states_tab1 = tab1.selectbox("**Select State for Top Transaction by District**", state)
    selected_states_tab2 = tab2.selectbox("**Select State for Top Transaction by Pincode**", state)    
    
    top_transaction_dist_df1 = top_transaction_dist_df[(top_transaction_dist_df['year']==selected_year) & (top_transaction_dist_df['quarter']==selected_quarter) & (top_transaction_dist_df['state']== selected_states_tab1)].reset_index(drop=True)
    fig_bar_top_dist = px.bar(
        top_transaction_dist_df1,
        x = 'dist_name',
        y = 'amount_top',
        color='avg_amount',
        text_auto='.2s',
        color_continuous_scale="Portland",
        title=f'Top District in "{selected_states_tab1}_{selected_quarter}_{selected_year}"'
        )
    fig_bar_top_dist.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    tab1.plotly_chart(fig_bar_top_dist) 

    top_transaction_pincode_df1 = top_transaction_pincode_df[(top_transaction_pincode_df['year']==selected_year) & (top_transaction_pincode_df['quarter']==selected_quarter) & (top_transaction_pincode_df['state']== selected_states_tab2)].reset_index(drop=True)
    top_transaction_pincode_df1.index = top_transaction_pincode_df1.index + 1

    top_transaction_pincode_df1.index = top_transaction_pincode_df1.index.rename("Sl.No")

    tab2.markdown(f'**Top Pincodes in "{selected_states_tab2}_{selected_quarter}_{selected_year}"**')
    tab2.dataframe(top_transaction_pincode_df1[['pincode','amount_top','avg_amount']],use_container_width=True)


    for i in state:
        top_transaction_dist_df3 = top_transaction_dist_df[(top_transaction_dist_df['year']==selected_year) & (top_transaction_dist_df['quarter']==selected_quarter) & (top_transaction_dist_df['state']== i)].reset_index(drop=True)
        fig_bar_top_dist = px.bar(
            top_transaction_dist_df3,
            x = 'dist_name',
            y = 'amount_top',
            color='avg_amount',
            text_auto='.2s',
            color_continuous_scale="Portland",
            title=f'Top District in "{i}_{selected_quarter}_{selected_year}"'
            )
        fig_bar_top_dist.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        tab3.plotly_chart(fig_bar_top_dist) 

    for i in state:
        top_transaction_pincode_df4 = top_transaction_pincode_df[(top_transaction_pincode_df['year']==selected_year) & (top_transaction_pincode_df['quarter']==selected_quarter) & (top_transaction_pincode_df['state']== i)].reset_index(drop=True)
        top_transaction_pincode_df4.index = top_transaction_pincode_df4.index + 1

        top_transaction_pincode_df4.index = top_transaction_pincode_df4.index.rename("Sl.No")

        tab4.markdown(f'**Top Pincodes in "{i}_{selected_quarter}_{selected_year}"**')
        tab4.dataframe(top_transaction_pincode_df4[['pincode','amount_top','avg_amount']],use_container_width=True)



elif Payments == 'Users':
    aggregated_user_sum =aggregated_user_df.groupby(by='year').sum().reset_index()
    
    registered_users = aggregated_user_sum['registeredUsers'].sum()


    fig_bar_aggregated_user_sum = px.bar(
        aggregated_user_sum,
        x = 'year',
        y = 'registeredUsers',
        color='appOpens',
        text_auto='.2s',
        color_continuous_scale="Portland",
        title="Registered Users over the years"
        )
    fig_bar_aggregated_user_sum.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_bar_aggregated_user_sum)
    st.subheader(f'**Total Registered Users = {registered_users:,}**')


    aggregated_user_df1 = aggregated_user_df[(aggregated_user_df['year'] == selected_year) & (aggregated_user_df['quarter'] == selected_quarter) ]

    fig = px.choropleth(
        aggregated_user_df1,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='state',
        hover_name = 'state',
        hover_data = ['appOpens'],        
        color='registeredUsers',
        color_continuous_scale="Portland",
        title=f'Registered Users till {selected_quarter}_{selected_year}'
    )
    fig.update_geos(fitbounds="locations", visible=False)

    st.plotly_chart(fig)

    fig_agg_pie= px.pie(
        aggregated_user_df1,
        values='registeredUsers',
        names='state',
        title=f'Registered Users till _{selected_quarter}_{selected_year}',
        hover_data = ['appOpens'] )
    fig_agg_pie.update_traces(textposition='inside', textinfo='percent+label')

    st.plotly_chart(fig_agg_pie)

    aggregated_user_df2 = aggregated_user_df.groupby(['state']).sum().reset_index()

    year = list(aggregated_user_df['year'].unique())

    fig_user = px.choropleth(
        aggregated_user_df2,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='state',
        hover_name = 'state',
        hover_data = ['appOpens'],        
        color='registeredUsers',
        color_continuous_scale="Portland",
        title=f'Registered Users till {year[-1]}'
    )
    fig_user.update_geos(fitbounds="locations", visible=False)

    st.plotly_chart(fig_user)


    st.subheader(f"Sum of User details for Each State till {year[-1]} ")

    fig_bar_aggregated_user = px.bar(
        aggregated_user_df2,
        x = 'state',
        y = 'registeredUsers',
        color='appOpens',
        text_auto='.2s',
        color_continuous_scale="Portland",
        )
    fig_bar_aggregated_user.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    
    st.plotly_chart(fig_bar_aggregated_user,use_container_width=True)    


    map_user_df1 = map_user_df[(map_user_df['year']==selected_year) & (map_user_df['quarter']==selected_quarter)].reset_index(drop=True)

    fig_map_user = px.treemap(
        map_user_df1 , 
        path = ['state','dist_name'], 
        values='registered_users',
        color='appOpens',
        color_continuous_scale="Greens",
        title=f"{selected_year}_{selected_quarter} Registered Users for each state"
        )
    fig_map_user.update_traces(textinfo='label+value+percent parent')
    st.plotly_chart(fig_map_user)    

    st.subheader(f"{selected_year} {selected_quarter} Top Registered Users in Each state by District and pincode") 

    tab1, tab2 = st.tabs(["Top District in Each State", "Top Pincode's in Each State"])
    

    for i in state:
        top_user_dist_df1 = top_user_dist_df[(top_user_dist_df['year']==selected_year) & (top_user_dist_df['quarter']==selected_quarter) & (top_user_dist_df['state']== i)].reset_index(drop=True)
        fig_bar_top_dist = px.bar(
            top_user_dist_df1,
            x = 'dist_name',
            y = 'registered_users',
            text_auto='.2s',
            color_continuous_scale="Portland",
            title=f'Top District in "{i}_{selected_quarter}_{selected_year}"'
            )
        fig_bar_top_dist.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        tab1.plotly_chart(fig_bar_top_dist) 

    for i in state:
        top_user_pincode_df1 = top_user_pincode_df[(top_user_pincode_df['year']==selected_year) & (top_user_pincode_df['quarter']==selected_quarter) & (top_user_pincode_df['state']== i)].reset_index(drop=True)
        top_user_pincode_df1.index = top_user_pincode_df1.index + 1

        top_user_pincode_df1.index = top_user_pincode_df1.index.rename("Sl.No")

        tab2.markdown(f'**Top Pincodes in "{i}_{selected_quarter}_{selected_year}"**')
        tab2.dataframe(top_user_pincode_df1[['pincode','registered_users']],use_container_width=True)