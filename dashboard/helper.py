class Analyzer:
   def __init__(self, df):
      self.df = df

   def create_dynamic_trends_products_df(self):
      self.df['quarter_year'] = self.df['order_approved_at'].dt.to_period('Q')
      self.df['month_year'] = self.df['order_purchase_timestamp'].dt.to_period('M')
      monthly_transactions = self.df.groupby(['month_year', 'product_category_name_english']).size().reset_index(name='total_transactions')
      return monthly_transactions

   def create_trend_product_quarterly_df(self):
      self.df['quarter_year'] = self.df['order_approved_at'].dt.to_period('Q')
      quarterly_transactions = self.df.groupby(['quarter_year', 'product_category_name_english']).size().reset_index(name='total_transactions')
      quarterly_transactions['rank'] = quarterly_transactions.groupby('quarter_year')['total_transactions'].rank(method='first', ascending=False)
      top3_quarterly_transactions = quarterly_transactions[quarterly_transactions['rank'] <= 3]

      return top3_quarterly_transactions

   def create_jumlah_order_produk_df(self):
      jumlah_order_produk_df = self.df.groupby("product_category_name_english")["product_id"].count().reset_index()
      jumlah_order_produk_df.rename(columns={
         "product_id": "products"
      }, inplace=True)
      jumlah_order_produk_df = jumlah_order_produk_df.sort_values(by='products', ascending=False)

      return jumlah_order_produk_df

   def create_daily_orders_df(self):
      daily_orders_df = self.df.resample(rule='D', on='order_approved_at').agg({
         "order_id": "nunique",
         "price": "sum"
      })
      daily_orders_df = daily_orders_df.reset_index()
      daily_orders_df.rename(columns={
         "order_id": "order_count",
         "price": "revenue"
      }, inplace=True)
      
      return daily_orders_df

   def create_order_status(self):
      order_status_df = self.df["order_status"].value_counts().sort_values(ascending=False)
      most_common_status = order_status_df.idxmax()

      return order_status_df, most_common_status

   def create_customer_sum_spend_money_df(self):
      sum_spend_df = self.df.resample(rule='D', on='order_approved_at').agg({
         "price": "sum"
      })
      sum_spend_df = sum_spend_df.reset_index()
      sum_spend_df.rename(columns={
         "price": "total_spend"
      }, inplace=True)

      return sum_spend_df

   def create_customer_review_score_df(self):
      review_scores = self.df
      return review_scores


   def create_bystate_df(self):
      bystate_df = self.df.groupby(by="customer_state").customer_id.nunique().reset_index()
      bystate_df.rename(columns={
         "customer_id": "customer_count"
      }, inplace=True)
      most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
      bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

      return bystate_df, most_common_state

   def create_revenue_top_product_df(self):
      revenue_top_product_df = self.df.groupby("product_category_name_english")["price"].sum().reset_index()
      revenue_top_product_df = revenue_top_product_df.sort_values(by='price', ascending=False)

      return revenue_top_product_df

   def create_revenue_top_quarter_df(self):
      jumlah_order_produk_df = self.df.groupby("product_category_name_english")["product_id"].count().reset_index()
      jumlah_order_produk_df.rename(columns={
         "product_id": "products"
      }, inplace=True)
      jumlah_order_produk_df = jumlah_order_produk_df.sort_values(by='products', ascending=False)

      annual_revenue = self.df.groupby([self.df['quarter_year'], 'product_category_name_english'])['price'].sum().reset_index()
      top5_product_categories = jumlah_order_produk_df['product_category_name_english'].head(5)
      annual_revenue = annual_revenue[annual_revenue['product_category_name_english'].isin(top5_product_categories)].reset_index(drop=True)
      annual_revenue['quarter_year'] = annual_revenue['quarter_year'].astype(str)
      # # Filter data untuk kategori produk yang diinginkan
      # annual_revenue = self.df.groupby([self.df['order_approved_at'].dt.year, 'product_category_name_english'])['price'].sum().reset_index()
      # annual_revenue.rename(columns={
      #    'order_approved_at': 'year'
      # }, inplace=True)
      # annual_revenue = annual_revenue.sort_values(by=['year', 'price'], ascending=[True, False])
      # annual_revenue = annual_revenue.groupby('year').head(3)

      return annual_revenue
