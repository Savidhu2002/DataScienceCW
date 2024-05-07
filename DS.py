import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

#reading csv files
orders=pd.read_csv('orders_cleaned.csv')
rules=pd.read_csv('association_rules.csv')

st.set_page_config(layout='wide')
st.title(':department_store: Minger Electronics Insights Dashboard')
col1,col2=st.columns((2))
#Adding dashboard filter
st.sidebar.title("Dashboard Filters")



#making tabs
Order_details, association_rules=st.tabs(['Order Details','Market Basket Analysis'])
with Order_details:
    st.header("Order Details")
    st.write(orders)
    #date picker
    orders['Order Date']=pd.to_datetime(orders['Order Date'])
    start_date=pd.to_datetime(orders['Order Date']).min()
    end_date=pd.to_datetime(orders['Order Date']).max()

    start=pd.to_datetime(st.sidebar.date_input('Pick start date',start_date))
    end=pd.to_datetime(st.sidebar.date_input('Pick end date',end_date))
    orders=orders[(orders['Order Date']>= start) & (orders['Order Date']<=end)].copy()
    
    # product category and market
    market=st.sidebar.selectbox('Pick your Market',orders['Market'].unique())
    category = st.sidebar.multiselect('Pick your category',orders['Category'].unique())
    
    #filtering the dashboard using the Market and product category
    if market and category:  
        filtered_data = orders[(orders["Market"].isin([market])) & (orders["Category"].isin(category))]
    elif market:  
        filtered_data = orders[orders["Market"].isin([market])]
    elif category:  
        # Retrieve subcategories belonging to the selected category
        subcategories = orders[orders["Category"].isin(category)]["Sub-Category"].unique().tolist()
        # Filter based on both category and its subcategories
        filtered_data = orders[(orders["Category"].isin(category)) | (orders["Sub-Category"].isin(subcategories))]
    else:
        filtered_data = orders.copy() 

    #Charts for the Orders dataset
   
    #Sales by sub category
    st.subheader('Sales by Sub Category')
    grp=filtered_data.groupby(by=['Sub-Category'],as_index=False)['Sales'].sum()
    fig1=px.bar(grp,x='Sub-Category',y='Sales', height=600,width=700)
        
    st.plotly_chart(fig1,use_container_width=True)

    
    #Sales by ship mode
    st.subheader ('Sales by ship mode')
    fig2=px.box(filtered_data,x='Ship Mode', y='Sales',height=400,width=600)
    st.plotly_chart(fig2,use_container_width=True)


    #Profit by country
    st.subheader('Profit by Country')
    grp=filtered_data.groupby(by=['Country'],as_index=False)['Profit'].sum()
    fig3=px.bar(grp,x="Country",y="Profit")
    st.plotly_chart(fig3,use_container_width=True)

    chart1,chart2= st.columns((2))
    with chart1:                          
        #scatter plot to show relationship between profit and sales
        scatter = px.scatter(orders, x = "Quantity", y = "Profit",size='Sales')
        scatter['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
                titlefont = dict(size=20),xaxis = dict(title="Sales",titlefont=dict(size=19)),
                yaxis = dict(title = "Profit", titlefont = dict(size=19)))
        st.plotly_chart(scatter,use_container_width=True)

    with chart2:
        #segemnt wise sales distribution
        st.subheader('Segment wise profit distribution')
        
        fig5=px.pie(orders,values="Sales",names='Segment')
        fig5.update_traces(text=orders['Segment'],textposition='outside')
        st.plotly_chart(fig5,use_container_width=True)


    #line chart to show sales over time
    filtered_data["month_year"] = filtered_data["Order Date"].dt.to_period("M")
    st.subheader('Sales over time')

    line = pd.DataFrame(filtered_data.groupby(filtered_data["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
    line = line.sort_values(by="month_year")
    fig4 = px.line(line, x = "month_year", y="Sales", labels = {"Sales": "Amount"},height=500, width = 1500,template="gridon")
    st.plotly_chart(fig4,use_container_width=True)
    
    
        

with association_rules:
    st.header("Market Basket Analysis Association Ruels")
    st.write(rules)
    
    #HEAT MAP
    import seaborn as sns
    st.subheader("Association Rules Heat Map")
    # Create the heatmap based on selected axes
    pivot_data = rules.pivot_table(index=rules['antecedents'], columns=rules['consequents'], values='lift')  

    heatfig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot_data, ax=ax, annot=True, cmap="viridis")  
    st.pyplot(heatfig)
        
    chart1, chart2 = st.columns((2))
    with chart1:
        fig6 = px.bar(rules, x='support', y='antecedents', orientation='h',title='Top Antecedents based on Support')
        st.plotly_chart(fig6,use_container_width=True)
    with chart2:
        fig7 = px.bar(rules, x='support', y='consequents', orientation='h',title='Top Consequents based on Support')
        st.plotly_chart(fig7,use_container_width=True)
    
    
        
    #treemap
    st.subheader("Hierarchical view of Antecedents with their Consequents based Support")
    fig10 = px.treemap(rules, path = ["antecedents","consequents"], values = "support",hover_data = ["support"],
                    color = "consequents")
    fig10.update_layout(width = 800, height = 650)
    st.plotly_chart(fig10, use_container_width=True)
