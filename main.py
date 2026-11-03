
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Lab 7 | Interactive Map Visualization | Made By Rivana Deborah Satriani",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# 2. COLOR PALETTE
# ==========================================================

NAVY = "#193B4A"
TEAL = "#6B9C9A"
LIGHT_TEAL = "#DCEAE7"
CORAL = "#D98272"
BACKGROUND = "#F5F7F6"
DARK_TEXT = "#263B43"
MUTED = "#73838A"

# ==========================================================
# 3. CUSTOM CSS
# ==========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background-color: #F5F7F6;
}

[data-testid="stSidebar"] {
    background-color: #193B4A;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF;
}

[data-testid="stSidebar"] label {
    color: #FFFFFF !important;
}

.main-title {
    color: #193B4A;
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 0;
}

.subtitle {
    color: #73838A;
    font-size: 14px;
    margin-top: 5px;
    margin-bottom: 25px;
}

.section-title {
    color: #193B4A;
    font-size: 24px;
    font-weight: 600;
    margin-top: 10px;
}

.description {
    color: #64767C;
    font-size: 14px;
    line-height: 1.8;
}

div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #E2E9E7;
    padding: 16px;
    border-radius: 10px;
}

div[data-testid="stMetricLabel"] {
    color: #73838A;
}

div[data-testid="stMetricValue"] {
    color: #193B4A;
}

hr {
    border: none;
    border-top: 1px solid #DCE5E2;
    margin-top: 20px;
    margin-bottom: 20px;
}

.stButton button {
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================================
# 4. LOAD GEOGRAPHICAL DATA
# ==========================================================

@st.cache_data
def load_data():

    file_path = (
        "ne_110m_admin_0_countries/"
        "ne_110m_admin_0_countries.shp"
    )

    data = gpd.read_file(file_path)

    # Identify population column
    if "pop_est" not in data.columns:

        if "POP_EST" in data.columns:
            data = data.rename(
                columns={"POP_EST": "pop_est"}
            )

        else:
            np.random.seed(0)

            data["pop_est"] = np.random.randint(
                1_000_000,
                1_000_000_000,
                size=len(data)
            )

    # Identify country name column
    possible_names = [
        "name",
        "NAME",
        "ADMIN",
        "NAME_EN"
    ]

    country_col = next(
        (
            col for col in possible_names
            if col in data.columns
        ),
        None
    )

    if country_col is None:
        raise ValueError(
            "Country name column could not be identified."
        )

    # Convert population to numeric values
    data["pop_est"] = pd.to_numeric(
        data["pop_est"],
        errors="coerce"
    )

    data["pop_est"] = data["pop_est"].fillna(
        data["pop_est"].median()
    )

    return data, country_col


try:

    gdf, country_col = load_data()

except Exception as error:

    st.error(
        f"Unable to load geographical dataset: {error}"
    )

    st.stop()


# ==========================================================
# 5. POPULATION DENSITY CALCULATION
# ==========================================================

# IMPORTANT:
# No @st.cache_data here because GeoDataFrame arguments
# can cause Streamlit hashing errors.

def calculate_density(data):

    # Convert geographic coordinates into an equal-area CRS
    equal_area = data.to_crs("EPSG:6933")

    # Calculate country area in square kilometres
    area_km2 = (
        equal_area.geometry.area / 1_000_000
    )

    # Calculate population density
    density = data["pop_est"] / area_km2

    # Handle invalid values
    density = density.replace(
        [np.inf, -np.inf],
        np.nan
    ).fillna(0)

    return density


gdf["pop_density"] = calculate_density(gdf)


# ==========================================================
# 6. SIDEBAR NAVIGATION
# ==========================================================

st.sidebar.markdown(
    """
    <h2 style="color:white; font-size:25px;">
        MAP STUDIO
    </h2>
    <p style="color:#B9D0D0; font-size:12px;">
        TFB3133 / TEB3133
        <br>
        Data Visualization
    </p>
    """,
    unsafe_allow_html=True
)

st.sidebar.divider()

st.sidebar.header("Map Configuration")

map_type = st.sidebar.radio(
    "Choose a Visualization",
    [
        "Map Cosmetics",
        "Map Visual Hierarchy",
        "Choropleth Map",
        "Geo Projection"
    ]
)

st.sidebar.divider()

st.sidebar.markdown(
    """
    <p style="color:#B9D0D0; font-size:12px;">
        Made By<br>
        Rivana Deborah Satriani
    </p>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# 7. MAIN DASHBOARD HEADER
# ==========================================================

st.markdown(
    '<p class="main-title">'
    'Interactive Map Visualization'
    '</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">'
    'Exploring geographical patterns through map design, '
    'data visualization, and spatial projections.'
    '</p>',
    unsafe_allow_html=True
)

# Overview metrics

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Countries and Territories",
        f"{len(gdf):,}"
    )

with col2:

    st.metric(
        "Estimated World Population",
        f"{gdf['pop_est'].sum() / 1_000_000_000:.2f} B"
    )

with col3:

    st.metric(
        "Visualization Modes",
        "04"
    )

st.divider()


# ==========================================================
# 8. MAP HELPER FUNCTIONS
# ==========================================================

def style_map(ax):

    ax.set_facecolor("#EDF2F1")
    ax.set_axis_off()

    for spine in ax.spines.values():
        spine.set_visible(False)


def display_map(fig):

    plt.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(fig)


# ==========================================================
# 9. MAP COSMETICS
# ==========================================================

if map_type == "Map Cosmetics":

    st.markdown(
        '<p class="section-title">'
        '01 | Map Cosmetics'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="description">'
        'Explore how visual styling improves map readability '
        'and presentation. Customize the country fill color '
        'and border thickness to create different map appearances.'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown("### Map Appearance Settings")

    col1, col2 = st.columns(2)

    with col1:

        country_color = st.selectbox(
            "Country Fill Color",
            [
                "Muted Teal",
                "Sky Blue",
                "Sage Green",
                "Soft Coral"
            ],
            index=0
        )

    with col2:

        border_width = st.slider(
            "Country Border Width",
            0.2,
            1.5,
            0.5,
            0.1
        )

    color_options = {
        "Muted Teal": "#8FBDB7",
        "Sky Blue": "#87BDE0",
        "Sage Green": "#A7BDA0",
        "Soft Coral": "#DFA092"
    }

    fig, ax = plt.subplots(
        figsize=(13, 7)
    )

    fig.patch.set_facecolor(BACKGROUND)

    gdf.plot(
        ax=ax,
        color=color_options[country_color],
        edgecolor="#425A60",
        linewidth=border_width
    )

    style_map(ax)

    ax.set_title(
        "World Map | Geographic Overview",
        fontsize=17,
        fontweight="bold",
        color=NAVY,
        pad=18
    )

    display_map(fig)

    st.caption(
        "Figure 1. World map with customized geographical styling."
    )


# ==========================================================
# 10. MAP VISUAL HIERARCHY
# ==========================================================

elif map_type == "Map Visual Hierarchy":

    st.markdown(
        '<p class="section-title">'
        '02 | Map Visual Hierarchy'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="description">'
        'Visual hierarchy helps viewers identify important '
        'geographical locations. Select countries to highlight '
        'them in coral while the remaining countries retain '
        'a neutral teal appearance.'
        '</p>',
        unsafe_allow_html=True
    )

    default_countries = [
        "Brazil",
        "India",
        "China",
        "Australia",
        "South Africa",
        "Russia"
    ]

    available_countries = sorted(
        gdf[country_col].dropna().unique().tolist()
    )

    valid_defaults = [
        country for country in default_countries
        if country in available_countries
    ]

    highlighted_countries = st.multiselect(
        "Select countries to highlight",
        options=available_countries,
        default=valid_defaults
    )

    plot_data = gdf.copy()

    plot_data["map_color"] = plot_data[
        country_col
    ].apply(
        lambda country:
        CORAL if country in highlighted_countries
        else "#A8C5C0"
    )

    fig, ax = plt.subplots(
        figsize=(13, 7)
    )

    fig.patch.set_facecolor(BACKGROUND)

    plot_data.plot(
        ax=ax,
        color=plot_data["map_color"],
        edgecolor="#425A60",
        linewidth=0.5
    )

    style_map(ax)

    ax.set_title(
        "Geographical Focus | Selected Countries",
        fontsize=17,
        fontweight="bold",
        color=NAVY,
        pad=18
    )

    display_map(fig)

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("**Highlighted Countries**")

        st.write(
            f"{len(highlighted_countries)} countries selected"
        )

    with col2:

        st.markdown("**Remaining Countries**")

        st.write(
            f"{len(gdf) - len(highlighted_countries)} countries"
        )

    st.caption(
        "Figure 2. Selected countries are emphasized "
        "using color contrast."
    )


# ==========================================================
# 11. CHOROPLETH MAP
# ==========================================================

elif map_type == "Choropleth Map":

    st.markdown(
        '<p class="section-title">'
        '03 | Choropleth Map'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="description">'
        'A choropleth map represents numerical data using '
        'different color intensities. This example illustrates '
        'estimated population density across countries.'
        '</p>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        color_choice = st.selectbox(
            "Choose Color Scheme",
            [
                "OrRd",
                "YlGn",
                "Blues",
                "Purples",
                "Greens"
            ],
            index=0
        )

    with col2:

        use_log_scale = st.checkbox(
            "Use Log Transformation",
            value=True
        )

    plot_data = gdf.copy()

    plot_data["display_density"] = (
        plot_data["pop_density"]
    )

    if use_log_scale:

        plot_data["display_density"] = np.log1p(
            plot_data["display_density"]
        )

    fig, ax = plt.subplots(
        figsize=(13, 7)
    )

    fig.patch.set_facecolor(BACKGROUND)

    plot_data.plot(
        column="display_density",
        cmap=color_choice,
        edgecolor="#52666B",
        linewidth=0.35,
        legend=True,
        ax=ax,
        legend_kwds={
            "label": (
                "Log Population Density"
                if use_log_scale
                else "Population Density (people/km²)"
            ),
            "shrink": 0.65
        },
        missing_kwds={
            "color": "#E0E5E3",
            "label": "No data"
        }
    )

    style_map(ax)

    ax.set_title(
        "Population Density by Country",
        fontsize=17,
        fontweight="bold",
        color=NAVY,
        pad=18
    )

    display_map(fig)

    st.caption(
        "Figure 3. Choropleth visualization of "
        "estimated population density."
    )

    if use_log_scale:

        st.info(
            "Log transformation is applied to reduce the "
            "effect of highly skewed population-density values."
        )

    else:

        st.info(
            "The map displays population density using "
            "original values in people per square kilometre."
        )


# ==========================================================
# 12. GEO PROJECTION
# ==========================================================

elif map_type == "Geo Projection":

    st.markdown(
        '<p class="section-title">'
        '04 | Geo Projection'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="description">'
        'Map projections transform the three-dimensional Earth '
        'into a two-dimensional representation. Different '
        'projections can change the appearance, shape, and '
        'relative size of geographical features.'
        '</p>',
        unsafe_allow_html=True
    )

    projection_options = {

        "Robinson": "ESRI:54030",

        "Mercator": "EPSG:3857",

        "Mollweide": "ESRI:54009",

        "World Equal Area": "EPSG:6933"

    }

    col1, col2 = st.columns(2)

    with col1:

        proj_choice = st.selectbox(
            "Select a Projection",
            list(projection_options.keys())
        )

    with col2:

        color_choice = st.selectbox(
            "Choose Color Scheme",
            [
                "OrRd",
                "YlGn",
                "Blues",
                "Purples",
                "Greens"
            ],
            index=2
        )

    use_log_scale = st.checkbox(
        "Use Log Transformation for Population Density",
        value=True
    )

    plot_data = gdf.copy()

    plot_data["display_density"] = (
        plot_data["pop_density"]
    )

    if use_log_scale:

        plot_data["display_density"] = np.log1p(
            plot_data["display_density"]
        )

    gdf_proj = plot_data.to_crs(
        projection_options[proj_choice]
    )

    fig, ax = plt.subplots(
        figsize=(13, 7)
    )

    fig.patch.set_facecolor(BACKGROUND)

    gdf_proj.plot(
        column="display_density",
        cmap=color_choice,
        edgecolor="#52666B",
        linewidth=0.35,
        legend=True,
        ax=ax,
        legend_kwds={
            "label": (
                "Log Population Density"
                if use_log_scale
                else "Population Density (people/km²)"
            ),
            "shrink": 0.65
        }
    )

    style_map(ax)

    ax.set_title(
        f"Population Density | {proj_choice} Projection",
        fontsize=17,
        fontweight="bold",
        color=NAVY,
        pad=18
    )

    display_map(fig)

    st.markdown("### Projection Information")

    projection_descriptions = {

        "Robinson": (
            "A compromise projection designed to provide "
            "a visually balanced representation of the world."
        ),

        "Mercator": (
            "A conformal projection that preserves local angles "
            "but significantly distorts areas near the poles."
        ),

        "Mollweide": (
            "An equal-area projection that preserves relative "
            "area across the world."
        ),

        "World Equal Area": (
            "An equal-area projection suitable for comparing "
            "the relative sizes of geographical regions."
        )

    }

    st.write(
        projection_descriptions[proj_choice]
    )

    st.caption(
        f"Figure 4. Population density displayed using "
        f"the {proj_choice} projection."
    )


# ==========================================================
# 13. DATASET INFORMATION
# ==========================================================

st.divider()

with st.expander("Explore Dataset Information"):

    st.markdown("### Geographic Dataset Preview")

    st.dataframe(
        gdf.drop(columns="geometry").head(10),
        use_container_width=True
    )

    st.markdown("### Dataset Details")

    st.write(
        "Total geographical records:",
        len(gdf)
    )

    st.write(
        "Country name field:",
        country_col
    )

    st.write(
        "Coordinate Reference System:",
        gdf.crs
    )

    st.markdown("### Available Variables")

    st.write(
        list(gdf.columns)
    )


# ==========================================================
# 14. FOOTER
# ==========================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; padding:15px;">
        <p style="color:#193B4A; font-weight:600;">
            Interactive Map Visualization | Lab 07
        </p>
        <p style="color:#73838A; font-size:12px;">
            TFB3133 / TEB3133 · Data Visualization · September 2026
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
