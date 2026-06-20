import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Database Connection
conn = sqlite3.connect("food_waste.db")

# Title
st.title("🍽️ Local Food Wastage Management System")

# KPI Cards
providers_count = pd.read_sql(
    "SELECT COUNT(*) as count FROM providers", conn
).iloc[0]["count"]

receivers_count = pd.read_sql(
    "SELECT COUNT(*) as count FROM receivers", conn
).iloc[0]["count"]

food_count = pd.read_sql(
    "SELECT COUNT(*) as count FROM food_listings", conn
).iloc[0]["count"]

claims_count = pd.read_sql(
    "SELECT COUNT(*) as count FROM claims", conn
).iloc[0]["count"]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Providers", providers_count)
col2.metric("Receivers", receivers_count)
col3.metric("Food Listings", food_count)
col4.metric("Claims", claims_count)

# Sidebar Menu
menu = st.sidebar.selectbox(
    "Select Option",
    [
        "Home",
        "Providers",
        "Receivers",
        "Food Listings",
        "Claims",
        "SQL Analysis"
    ]
)

# Home Page
if menu == "Home":

    st.header("📊 Dashboard")

    food_df = pd.read_sql(
        "SELECT * FROM food_listings",
        conn
    )

    # Filters
    city = st.selectbox(
        "Select City",
        ["All"] + sorted(
            food_df["field7"].dropna().unique().tolist()
        )
    )

    food_type = st.selectbox(
        "Select Food Type",
        ["All"] + sorted(
            food_df["field3"].dropna().unique().tolist()
        )
    )

    # Apply filters
    filtered_df = food_df.copy()

    if city != "All":
        filtered_df = filtered_df[
            filtered_df["field7"] == city
        ]

    if food_type != "All":
        filtered_df = filtered_df[
            filtered_df["field3"] == food_type
        ]

    st.success(
        f"Total Records: {len(filtered_df)}"
    )

    # Chart 1 - System Overview
    chart_df = pd.DataFrame({
        "Category": ["Providers", "Receivers", "Food Listings", "Claims"],
        "Count": [
            providers_count,
            receivers_count,
            food_count,
            claims_count
        ]
    })

    st.subheader("System Overview")

    st.bar_chart(
        chart_df.set_index("Category")
    )

    # Chart 2 - Food Type Distribution
    st.subheader("Food Type Distribution")

    food_df = pd.read_sql(
        "SELECT * FROM food_listings",
        conn
    )

    food_counts = food_df["field3"].value_counts()

    st.bar_chart(food_counts)

    # Chart 3 - Top Locations
    st.subheader("Top Locations")

    location_counts = food_df["field7"].value_counts().head(10)

    st.bar_chart(location_counts)

    # Chart 4 - Food Share Pie Chart
    st.subheader("Food Category Share")

    fig, ax = plt.subplots()

    food_counts.head(8).plot(
        kind="pie",
        autopct="%1.1f%%",
        ax=ax
    )

    ax.set_ylabel("")

    st.pyplot(fig)
# Providers Page
elif menu == "Providers":
    st.header("Providers")

    df = pd.read_sql("SELECT * FROM providers", conn)

    search = st.text_input("Search Provider Name")

    if search:
        df = df[df["Name"].str.contains(search, case=False, na=False)]

    st.dataframe(df)
# Receivers Page
elif menu == "Receivers":
    st.header("Receivers")
    df = pd.read_sql("SELECT * FROM receivers", conn)
    st.dataframe(df)

# Food Listings Page
elif menu == "Food Listings":

    st.header("Food Summary Data")

    df = pd.read_sql(
        "SELECT * FROM food_listings",
        conn
    )

    # Sidebar Filters
    city = st.sidebar.selectbox(
        "Select City",
        ["All"] + sorted(
            df["field7"].dropna().unique().tolist()
        )
    )

    provider = st.sidebar.selectbox(
        "Select Provider",
        ["All"] + sorted(
            df["field9"].dropna().unique().tolist()
        )
    )

    meal = st.sidebar.selectbox(
        "Select Meal Type",
        ["All"] + sorted(
            df["field4"].dropna().unique().tolist()
        )
    )

    food = st.sidebar.selectbox(
        "Select Food Type",
        ["All"] + sorted(
            df["field3"].dropna().unique().tolist()
        )
    )

    if city != "All":
        df = df[df["field7"] == city]

    if provider != "All":
        df = df[df["field9"] == provider]

    if meal != "All":
        df = df[df["field4"] == meal]

    if food != "All":
        df = df[df["field3"] == food]

    st.success(f"Total Records: {len(df)}")

    st.write(df.shape)

    st.dataframe(
        df,
        use_container_width=True,
        height=500
    )
# Claims Page
elif menu == "Claims":
    st.header("Claims")
    df = pd.read_sql("SELECT * FROM claims", conn)
    st.dataframe(df)
# SQL Analysis Page
elif menu == "SQL Analysis":

    st.header("📊 SQL Analysis")

    # Query 1
    st.subheader("1. Providers and Receivers in Each City")

    query1 = """
    SELECT
        p.City,
        COUNT(DISTINCT p.Provider_ID) AS Total_Providers,
        COUNT(DISTINCT r.Receiver_ID) AS Total_Receivers
    FROM providers p
    LEFT JOIN receivers r
    ON p.City = r.City
    GROUP BY p.City
    """

    df1 = pd.read_sql(query1, conn)

    st.dataframe(df1)

    st.bar_chart(df1.set_index("City"))

    # Query 2
    st.subheader("2. Provider Type Contributing Most Food")

    query2 = """
    SELECT
        Provider_Type,
        SUM(Quantity) AS Total_Food
    FROM food_listings
    GROUP BY Provider_Type
    ORDER BY Total_Food DESC
    """

    df2 = pd.read_sql(query2, conn)

    st.dataframe(df2)

    st.bar_chart(df2.set_index("Provider_Type"))

    # Query 3
    st.subheader("3. Total Quantity of Food Available")

    query3 = """
    SELECT
        SUM(Quantity) AS Total_Food_Available
    FROM food_listings
    """

    df3 = pd.read_sql(query3, conn)

    st.dataframe(df3)

