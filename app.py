import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title = "SuperSale Insights",
                   page_icon = ":bar_chart:",
                   layout = "wide")
st.title("📈  SuperSale Insights: Analyzing Supermarket Sales\n")
st.markdown("") # Adding a new line
#st.subheader(" ")

st.markdown("---") # Divider

# --- LOAD DATA ---

# Storing data to cache to avoid the repetitive loading of dataset from excel each time.
@st.cache_data
def get_data_from_excel():
    excel_file = 'super_sales.xlsx'
    sheet_name = 'Data'
    df = pd.read_excel(excel_file,
                    sheet_name = sheet_name,
                    skiprows = 3,
                    usecols = 'B:R',
                    nrows = 1000)
    # Add hour column to the dataframe
    df["hour"] = pd.to_datetime(df["Time"], format = "%H:%M:%S").dt.hour
    return df
df = get_data_from_excel()

# --- SIDEBAR ---
st.sidebar.header("Select filter here: ")
city = st.sidebar.multiselect(
    "Select the City: ",
    options = df["City"].unique(),
    default = df["City"].unique()
)

gender = st.sidebar.multiselect(
    "Select the Gender: ",
    options = df["Gender"].unique(),
    default = df["Gender"].unique()
)

customer_type = st.sidebar.multiselect(
    "Select the Customer Type: ",
    options = df["Customer_type"].unique(),
    default = df["Customer_type"].unique()
)

# --- STREAMLIT SLIDER
st.sidebar.subheader("Select time range (in hours):")
rounded_hours = sorted(df["hour"].unique())
rounded_hour_selection = st.sidebar.slider("", min_value=min(rounded_hours), max_value=max(rounded_hours),
                                           value=(min(rounded_hours), max(rounded_hours)))
st.sidebar.write("Hours between:", rounded_hour_selection)

df_selection = df.query(
    "City == @city & Gender == @gender & Customer_type == @customer_type &" 
    "hour >= @rounded_hour_selection[0] & hour <= @rounded_hour_selection[1]"
)

# --- MAIN PAGE ---

# --- TOP KPI ---
total_sales = int(df_selection["Total"].sum())
avg_rating = round(df_selection["Rating"].mean(),1)
star_rating = ":star:" * int(round(avg_rating, 0))

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Sales: ")
    st.subheader(f"US $ {total_sales:,}")
with right_column:
    st.subheader("Average Rating: ")
    st.subheader(f"{avg_rating} {star_rating}")

st.markdown("---") # Divider

#st.markdown("##### Dataset")
#st.dataframe(df_selection.head(5))

# create an Preview by expanding
with st.expander("Data Preview"):
    st.dataframe(df)

# dropping null values from the dataset
df_selection.dropna(inplace = True)

# --- DATA VISUALIZATION
sales_by_payment = (
    df_selection.groupby(by=["Payment"]).sum()[["Total"]]
)
fig_sales_by_payment = px.pie(sales_by_payment,
                              names = sales_by_payment.index,
                              values = "Total",
                              title = "<b>Sales by Product Payment</b>",
                              color_discrete_sequence=["#ef4444","#f87171","#fca5a5"]
                            )
fig_sales_by_payment.update_layout(
        legend=dict(orientation="h", 
        yanchor="bottom", 
        y=-0.2, 
        xanchor="left", 
        x=0))
#st.plotly_chart(fig_sales_by_payment)

product_by_quantity = (
    df_selection.groupby(by=["Product line"]).sum().reset_index()
)
fig_product_by_quantity = px.line(product_by_quantity,
                                  x = "Quantity",
                                  y = "Product line",
                                  title = "<b>Product by Quantity Sales</b>",
                                  markers = True,
                                  text = "Quantity",
                                  color_discrete_sequence=["#ef4444"] * len(product_by_quantity),
                                  template = "plotly_white"
                                )
fig_product_by_quantity.update_layout(
    plot_bgcolor = "rgba(0,0,0,0)",
    yaxis = (dict(showgrid=False))
)
#st.plotly_chart(fig_product_by_quantity)

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_sales_by_payment, use_container_width=True)
right_column.plotly_chart(fig_product_by_quantity, use_container_width=True)

sales_by_product = (
    df_selection.groupby(by=["Product line"]).sum()[["Total"]].sort_values(by="Total")
)
fig_sales_by_product = px.bar(sales_by_product,
                              x = "Total",
                              y = sales_by_product.index,
                              orientation = "h",
                              title = "<b>Sales by Product Line</b>",
                              color_discrete_sequence=["#ef4444"] * len(sales_by_product),
                              template = "plotly_white")
fig_sales_by_product.update_layout(
    plot_bgcolor = "rgba(0,0,0,0)",
    xaxis = (dict(showgrid=False))
)
#st.plotly_chart(fig_sales_by_product)

sales_by_hour = (
    df_selection.groupby(by=["hour"]).sum()[["Total"]]
)
fig_sales_by_hour = px.bar(sales_by_hour,
                              x = sales_by_hour.index,
                              y = "Total",
                              title = "<b>Sales by hour</b>",
                              color_discrete_sequence=["#ef4444"] * len(sales_by_hour),
                              template = "plotly_white")
fig_sales_by_hour.update_layout(
    xaxis = dict(tickmode = "linear"),
    plot_bgcolor = "rgba(0,0,0,0)",
    yaxis = (dict(showgrid=False))
)
#st.plotly_chart(fig_sales_by_hour)

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_sales_by_product, use_container_width=True)
right_column.plotly_chart(fig_sales_by_hour, use_container_width=True)

sales_by_rating = (
    df_selection.groupby(by=["Rating"]).count()[["Total"]]
)
fig_sales_by_rating = px.scatter(sales_by_rating,
                                 x = sales_by_rating.index,
                                 y = "Total",
                                 title = "<b>Rating by Sales</b>",
                                 color_discrete_sequence=["#ef4444"] * len(sales_by_hour)
                                )
#st.plotly_chart(fig_sales_by_rating)

product_by_rating = (
    df_selection.groupby(by=["Product line"]).count().reset_index()
)
fig_product_by_rating = px.area(product_by_rating,
                                x = "Product line",
                                y = "Rating",
                                title = "<b>Product by Rating</b>",
                                color_discrete_sequence=["#ef4444"] * len(sales_by_hour),
                                labels={'Rating': 'Rating', 'Product line': 'Product Line'},
                                template='plotly_white',
                                )
#st.plotly_chart(fig_product_by_rating)

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_sales_by_rating, use_container_width=True)
right_column.plotly_chart(fig_product_by_rating, use_container_width=True)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)








