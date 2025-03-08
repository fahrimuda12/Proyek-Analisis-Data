import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import streamlit as st
import urllib
from helper import Analyzer
from babel.numbers import format_currency
sns.set(style='white')

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("./dashboard/main_data.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)


for col in datetime_cols:
   all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
   # Title
   st.title("Shopingku")
   st.image("./dashboard/logo.jpg", width=100)

   # Date Range
   start_date, end_date = st.date_input(
       label="Select Date Range",
       value=[min_date, max_date],
       min_value=min_date,
       max_value=max_date
   )

# Main
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

helper = Analyzer(main_df)

# Product Helper
quartely_trend_products_df = helper.create_trend_product_quarterly_df()
jumlah_order_produk_df = helper.create_jumlah_order_produk_df()

# Order Helper
daily_orders_df = helper.create_daily_orders_df()
order_status, common_status = helper.create_order_status()

# Customer Helper
sum_spend_df = helper.create_customer_sum_spend_money_df()
review_score, common_score = helper.create_customer_review_score_df()
state, most_common_state = helper.create_bystate_df()

# Revenue Helper
revenue_top_product_df = helper.create_revenue_top_product_df()
revenue_top_yearly_df = helper.create_revenue_top_yearly_df()

# Title
st.header("Shopingku Dashboard :convenience_store:")

# menu bar
product_menu, order_menu, customer_menu, reveneu_menu = st.tabs(["Product", "Order", "Customer", "Revenue"])

with product_menu:
   # Quarterly Trends
   st.subheader("Top 3 Quarterly Trends")

   plt.figure(figsize=(10, 5))
   sns.barplot(data=quartely_trend_products_df, x='quarter_year', y='total_transactions', hue='product_category_name_english', errorbar=None, dodge=False)

   quarter_labels = [f"{str(label).replace('Q', '-Q')} \n ({label.start_time.strftime('%b')}-{label.end_time.strftime('%b')})" for label in quartely_trend_products_df['quarter_year'].unique()]
   plt.gca().set_xticklabels(quarter_labels)
   plt.xlabel('Quarter-Year')
   plt.ylabel('Total Transactions')
   plt.xticks(rotation=90)
   plt.legend(title='Product Category', bbox_to_anchor=(1.05, 1), loc='upper left')
   plt.tight_layout()
   st.pyplot(plt)

   # Order Items
   st.subheader("Most Ordered Product Items")
   col1, col2 = st.columns(2)

   with col1:
      total_items = jumlah_order_produk_df["products"].sum()
      st.markdown(f"Total Items: **{total_items}**")

   with col2:
      avg_items = jumlah_order_produk_df["products"].mean()
      st.markdown(f"Average Items: **{avg_items:.2f}**")

   fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

   colors = ["#068DA9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

   colors = ["#068DA9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

   sns.barplot(x="products", y="product_category_name_english", data=jumlah_order_produk_df.head(5), palette=colors, ax=ax[0])
   ax[0].set_ylabel(None)
   ax[0].set_xlabel("Number of Sales", fontsize=30)
   ax[0].set_title("Produk Terlaris", loc="center", fontsize=50)
   ax[0].tick_params(axis ='y', labelsize=35)
   ax[0].tick_params(axis ='x', labelsize=30)

   sns.barplot(x="products", y="product_category_name_english", data=jumlah_order_produk_df.sort_values(by="products", ascending=True).head(5), palette=colors, ax=ax[1])
   ax[1].set_ylabel(None)
   ax[1].set_xlabel("Number of Sales", fontsize=30)
   ax[1].invert_xaxis()
   ax[1].yaxis.set_label_position("right")
   ax[1].yaxis.tick_right()
   ax[1].set_title("Produk Sedikit Terjual", loc="center", fontsize=50)
   ax[1].tick_params(axis='y', labelsize=35)
   ax[1].tick_params(axis='x', labelsize=30)
   st.pyplot(fig)

with order_menu:
   # Daily Orders
   st.subheader("Daily Orders")

   col1, col2 = st.columns(2)

   with col1:
      total_order = daily_orders_df["order_count"].sum()
      st.markdown(f"Total Order: **{total_order}**")

   with col2:
      total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
      st.markdown(f"Total Revenue: **{total_revenue}**")

   fig, ax = plt.subplots(figsize=(12, 6))
   ax.plot(
      daily_orders_df["order_approved_at"],
      daily_orders_df["order_count"],
      marker="o",
      linewidth=2,
      color="#90CAF9"
   )
   ax.tick_params(axis="x", rotation=45)
   ax.tick_params(axis="y", labelsize=15)
   st.pyplot(fig)

   # order status
   st.subheader("Order Status")

   common_status_ = order_status.value_counts().index[0]
   st.markdown(f"Most Common Order Status: **{common_status_}**")
   fig, ax = plt.subplots(figsize=(12, 6))
   sns.barplot(x=order_status.index,
               y=order_status.values,
               order=order_status.index,
               palette=["#068DA9" if score == common_status else "#D3D3D3" for score in order_status.index]
               )
   
   plt.title("Order Status", fontsize=15)
   plt.xlabel("Status")
   plt.ylabel("Count")
   plt.xticks(fontsize=12)
   st.pyplot(fig)

with customer_menu:
   # Customer Spend Money
   st.subheader("Customer Spend Money")
   col1, col2 = st.columns(2)

   with col1:
      total_spend = format_currency(sum_spend_df["total_spend"].sum(), "IDR", locale="id_ID")
      st.markdown(f"Total Spend: **{total_spend}**")

   with col2:
      avg_spend = format_currency(sum_spend_df["total_spend"].mean(), "IDR", locale="id_ID")
      st.markdown(f"Average Spend: **{avg_spend}**")

   fig, ax = plt.subplots(figsize=(12, 6))
   ax.plot(
      sum_spend_df["order_approved_at"],
      sum_spend_df["total_spend"],
      marker="o",
      linewidth=2,
      color="#90CAF9"
   )
   ax.tick_params(axis="x", rotation=45)
   ax.tick_params(axis="y", labelsize=15)
   st.pyplot(fig)

   # Customer Common State
   st.subheader("Customer Common State")

   most_common_state = state.customer_state.value_counts().index[0]
   st.markdown(f"Most Common State: **{most_common_state}**")
   fig, ax = plt.subplots(figsize=(12, 6))
   sns.barplot(x=state.customer_state.value_counts().index,
               y=state.customer_count.values, 
               data=state,
               palette=["#068DA9" if score == most_common_state else "#D3D3D3" for score in state.customer_state.value_counts().index]
               )
   plt.title("Number customers from State", fontsize=15)
   plt.xlabel("State")
   plt.ylabel("Number of Customers")
   plt.xticks(fontsize=12)
   st.pyplot(fig)

   # Review Score
   st.subheader("Review Score")
   col1,col2 = st.columns(2)

   with col1:
      avg_review_score = review_score.mean()
      st.markdown(f"Average Review Score: **{avg_review_score}**")

   with col2:
      most_common_review_score = review_score.value_counts().index[0]
      st.markdown(f"Most Common Review Score: **{most_common_review_score}**")

   fig, ax = plt.subplots(figsize=(12, 6))
   sns.barplot(x=review_score.index, 
               y=review_score.values, 
               order=review_score.index,
               palette=["#068DA9" if score == common_score else "#D3D3D3" for score in review_score.index]
               )

   plt.title("Rating by customers for service", fontsize=15)
   plt.xlabel("Rating")
   plt.ylabel("Count")
   plt.xticks(fontsize=12)
   st.pyplot(fig)

with reveneu_menu:
   # Revenue Top Product
   st.subheader("Revenue Top Product")
   
   revenue_top_product_df["payment_value"] = revenue_top_product_df["payment_value"].apply(lambda x: format_currency(x, "IDR", locale="id_ID"))
   
   fig, ax = plt.subplots(figsize=(12, 6))
   sns.barplot(x="payment_value", y="product_category_name_english", data=revenue_top_product_df.head(5))
   plt.title("Top 5 Revenue Product", fontsize=15)
   plt.xlabel("Revenue")
   plt.ylabel("Product Category")
   st.pyplot(fig)

   # revenue Top Yearly
   st.subheader("Revenue Top Yearly")

   # Create a line plot for the top 3 products by yearly revenue
   fig, ax = plt.subplots(figsize=(12, 6))
   sns.lineplot(x='year', y='payment_value', hue='product_category_name_english', data=revenue_top_yearly_df, marker='o', palette='viridis')
   plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

   # Add titles and labels
   plt.title('Yearly Revenue of Top 3 Product Categories', fontsize=16)
   plt.xlabel('Year', fontsize=14)
   plt.ylabel('Total Revenue', fontsize=14)
   plt.legend(title='Product Category', bbox_to_anchor=(1.05, 1), loc='upper left')

   # Format y-axis as dollar
   formatter = ticker.FuncFormatter(lambda x, pos: f'${x:,.0f}')
   plt.gca().yaxis.set_major_formatter(formatter)
   st.pyplot(fig)