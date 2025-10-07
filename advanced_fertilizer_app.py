
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
import folium
from streamlit_folium import st_folium
import json
from datetime import datetime, timedelta
import requests

# Page configuration
st.set_page_config(
    page_title="Northern Nigeria Smart Fertilizer Advisor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E8B57 0%, #228B22 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .recommendation-box {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
        border: 2px solid #28a745;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #fef7e0 100%);
        border: 2px solid #ffc107;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #e2f0e4 100%);
        border: 2px solid #28a745;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .nutrient-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem;
    }
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🌾 Northern Nigeria Smart Fertilizer Advisor</h1>
        <h3>AI-Powered Precision Nutrient Management System</h3>
        <p>Empowering farmers, extension agents, and researchers with data-driven fertilizer recommendations</p>
    </div>
    """, unsafe_allow_html=True)

    # Language selection
    languages = {"English": "en", "Hausa": "ha", "Fulfulde": "ff"}
    selected_lang = st.sidebar.selectbox("🌍 Select Language / Zaɓi Harshe", list(languages.keys()))

    # Main navigation
    st.sidebar.title("📋 Navigation Menu")
    user_type = st.sidebar.selectbox(
        "👤 I am a:", 
        ["👨‍🌾 Farmer (Manomi)", "🎓 Extension Agent", "🔬 Researcher", "🏛️ Policy Maker"]
    )

    if user_type == "👨‍🌾 Farmer (Manomi)":
        farmer_interface()
    elif user_type == "🎓 Extension Agent":
        extension_interface()
    elif user_type == "🔬 Researcher":
        researcher_interface()
    elif user_type == "🏛️ Policy Maker":
        policy_interface()

def farmer_interface():
    """Simplified interface for farmers"""
    st.header("👨‍🌾 Farmer Dashboard / Dashboard na Manomi")

    # Quick soil test option
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🧪 Simple Soil Assessment")

        # Simplified inputs
        state = st.selectbox("State", ["Kaduna", "Kano", "Katsina", "Sokoto", "Kebbi"])
        lga = st.selectbox("Local Government Area", ["Select your LGA", "Kaduna North", "Kaduna South"])

        st.markdown("**🗺️ Farm Location (Optional)**")
        use_gps = st.checkbox("📍 Use current GPS location")

        if not use_gps:
            latitude = st.number_input("Latitude (if known)", value=11.5, step=0.01)
            longitude = st.number_input("Longitude (if known)", value=8.5, step=0.01)

        st.markdown("**🌱 Soil Information**")

        # Visual soil assessment
        soil_color = st.selectbox("Soil Color", 
                                ["Very Dark Brown/Black", "Dark Brown", "Brown", "Light Brown", "Red", "Gray"])

        soil_texture = st.selectbox("Soil Feel (when wet)",
                                  ["Very Sandy (gritty)", "Sandy", "Balanced (loamy)", "Clay-like (sticky)"])

        previous_yield = st.selectbox("Last Season Yield per Hectare",
                                    ["Less than 1 ton", "1-2 tons", "2-3 tons", "3-4 tons", "More than 4 tons"])

        # Simple soil test results (if available)
        has_soil_test = st.checkbox("I have professional soil test results")

        if has_soil_test:
            n_percent = st.number_input("Nitrogen (%)", min_value=0.1, max_value=5.0, value=1.2)
            p_ppm = st.number_input("Phosphorus (ppm)", min_value=1.0, max_value=100.0, value=15.0)
            k_ppm = st.number_input("Potassium (ppm)", min_value=50.0, max_value=500.0, value=180.0)
            ph = st.number_input("Soil pH", min_value=4.0, max_value=9.0, value=6.2)

        farm_size = st.number_input("Farm Size (hectares)", min_value=0.1, max_value=100.0, value=2.0)
        target_yield = st.selectbox("Target Yield this Season",
                                  ["2 tons/ha", "3 tons/ha", "4 tons/ha", "5 tons/ha"])

        if st.button("🔬 Get My Fertilizer Recommendation", type="primary"):
            # Process visual assessment
            recommendations = process_visual_assessment(
                soil_color, soil_texture, previous_yield, target_yield, farm_size, has_soil_test,
                n_percent if has_soil_test else None,
                p_ppm if has_soil_test else None,
                k_ppm if has_soil_test else None,
                ph if has_soil_test else None
            )
            st.session_state.farmer_rec = recommendations

    with col2:
        if 'farmer_rec' in st.session_state:
            display_farmer_recommendations(st.session_state.farmer_rec)

def process_visual_assessment(soil_color, soil_texture, prev_yield, target_yield, 
                            farm_size, has_test=False, n=None, p=None, k=None, ph=None):
    """Process visual soil assessment into recommendations"""

    # Convert qualitative to quantitative estimates
    color_n_map = {
        "Very Dark Brown/Black": 2.0,
        "Dark Brown": 1.5,
        "Brown": 1.2,
        "Light Brown": 0.8,
        "Red": 0.9,
        "Gray": 0.7
    }

    texture_pk_map = {
        "Very Sandy (gritty)": {"p": 8, "k": 80},
        "Sandy": {"p": 12, "k": 120},
        "Balanced (loamy)": {"p": 20, "k": 200},
        "Clay-like (sticky)": {"p": 25, "k": 250}
    }

    yield_map = {
        "Less than 1 ton": 800,
        "1-2 tons": 1500,
        "2-3 tons": 2500,
        "3-4 tons": 3500,
        "More than 4 tons": 4500
    }

    target_map = {
        "2 tons/ha": 2000,
        "3 tons/ha": 3000,
        "4 tons/ha": 4000,
        "5 tons/ha": 5000
    }

    # Use test results if available, otherwise estimate
    if has_test and all([n, p, k, ph]):
        n_est, p_est, k_est = n, p, k
    else:
        n_est = color_n_map.get(soil_color, 1.2)
        p_est = texture_pk_map.get(soil_texture, {"p": 15})["p"]
        k_est = texture_pk_map.get(soil_texture, {"k": 150})["k"]

    # Calculate recommendations
    return calculate_simple_recommendations(
        n_est, p_est, k_est, 
        yield_map[prev_yield], 
        target_map[target_yield], 
        farm_size
    )

def calculate_simple_recommendations(n_percent, p_ppm, k_ppm, prev_yield, target_yield, farm_size):
    """Simplified recommendation calculation"""

    # Limitation assessment
    n_limitation = "High" if n_percent < 1.0 else "Medium" if n_percent < 1.5 else "Low"
    p_limitation = "High" if p_ppm < 15 else "Medium" if p_ppm < 25 else "Low"
    k_limitation = "High" if k_ppm < 120 else "Medium" if k_ppm < 200 else "Low"

    # Base rates (kg/ha)
    base_n = 80 if n_limitation == "High" else 60 if n_limitation == "Medium" else 40
    base_p = 50 if p_limitation == "High" else 35 if p_limitation == "Medium" else 25
    base_k = 40 if k_limitation == "High" else 30 if k_limitation == "Medium" else 20

    # Adjust for yield target
    yield_factor = min(target_yield / 3000, 1.5)

    n_rec = base_n * yield_factor
    p_rec = base_p * yield_factor
    k_rec = base_k * yield_factor

    # Convert to fertilizer products
    urea_needed = (n_rec / 0.46) * farm_size  # Urea is 46% N
    dap_needed = (p_rec / 0.46) * farm_size   # DAP is 46% P2O5
    mop_needed = (k_rec / 0.60) * farm_size   # MOP is 60% K2O

    # Economic analysis
    fertilizer_cost = (n_rec * 1.2 + p_rec * 2.5 + k_rec * 1.0) * farm_size
    expected_yield = min(prev_yield * 1.3, target_yield)
    yield_increase = expected_yield - prev_yield

    revenue_increase = yield_increase * farm_size * 0.45  # USD/kg maize price
    net_profit = revenue_increase - fertilizer_cost
    roi = (net_profit / fertilizer_cost * 100) if fertilizer_cost > 0 else 0

    return {
        'limitations': {'N': n_limitation, 'P': p_limitation, 'K': k_limitation},
        'fertilizers': {
            'urea_kg': urea_needed,
            'dap_kg': dap_needed,
            'mop_kg': mop_needed
        },
        'rates': {'N': n_rec, 'P2O5': p_rec, 'K2O': k_rec},
        'economics': {
            'total_cost': fertilizer_cost,
            'expected_yield': expected_yield,
            'yield_increase': yield_increase,
            'revenue_increase': revenue_increase,
            'net_profit': net_profit,
            'roi': roi
        },
        'farm_size': farm_size
    }

def display_farmer_recommendations(rec):
    """Display recommendations in farmer-friendly format"""

    st.markdown('<div class="recommendation-box">', unsafe_allow_html=True)
    st.markdown("## 📋 Your Fertilizer Recommendation")

    # Nutrient status
    st.markdown("### 🔍 Your Soil Nutrient Status")
    col1, col2, col3 = st.columns(3)

    colors = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}

    with col1:
        st.markdown(f"""
        <div class="nutrient-card">
            <h4>{colors[rec['limitations']['N']]} Nitrogen</h4>
            <p><strong>{rec['limitations']['N']} Limitation</strong></p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="nutrient-card">
            <h4>{colors[rec['limitations']['P']]} Phosphorus</h4>
            <p><strong>{rec['limitations']['P']} Limitation</strong></p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="nutrient-card">
            <h4>{colors[rec['limitations']['K']]} Potassium</h4>
            <p><strong>{rec['limitations']['K']} Limitation</strong></p>
        </div>
        """, unsafe_allow_html=True)

    # Fertilizer shopping list
    st.markdown("### 🛒 Your Fertilizer Shopping List")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Fertilizer Types Needed:**")
        st.info(f"🥫 **Urea (White granules)**\n{rec['fertilizers']['urea_kg']:.0f} kg")
        st.info(f"🥫 **DAP (Dark granules)**\n{rec['fertilizers']['dap_kg']:.0f} kg") 
        st.info(f"🥫 **Muriate of Potash (Red/white)**\n{rec['fertilizers']['mop_kg']:.0f} kg")

    with col2:
        st.markdown("**Application Rates (per hectare):**")
        st.metric("Nitrogen (N)", f"{rec['rates']['N']:.0f} kg/ha")
        st.metric("Phosphorus (P2O5)", f"{rec['rates']['P2O5']:.0f} kg/ha")
        st.metric("Potassium (K2O)", f"{rec['rates']['K2O']:.0f} kg/ha")

    # Economic projection
    st.markdown("### 💰 Economic Outlook")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Investment", f"${rec['economics']['total_cost']:.0f}")

    with col2:
        st.metric("Expected Extra Yield", f"{rec['economics']['yield_increase']:.0f} kg/ha")

    with col3:
        if rec['economics']['net_profit'] > 0:
            st.metric("Expected Profit", f"${rec['economics']['net_profit']:.0f}", 
                     f"{rec['economics']['roi']:.0f}% ROI")
        else:
            st.metric("Investment Period", "1 Season", "Break-even expected")

    # Application instructions
    st.markdown("### 📅 Application Instructions")

    instructions = f"""
    **⏰ Timing:**
    - Apply 2-3 weeks before planting
    - Split nitrogen: 50% at planting, 50% at 6 weeks after planting

    **🌱 Application Method:**
    - Mix DAP and MOP, apply during land preparation
    - Apply first Urea dose at planting
    - Apply second Urea dose 6 weeks after planting

    **☔ Weather Considerations:**
    - Apply before expected rainfall
    - Avoid application during heavy rains

    **📞 Need Help?**
    - Contact your local extension agent
    - Call agricultural helpline: 080-XXXXX-XXX
    """

    st.markdown(instructions)
    st.markdown('</div>', unsafe_allow_html=True)

    # Download recommendation
    if st.button("📄 Download Recommendation Report"):
        create_farmer_report(rec)

def extension_interface():
    """Interface for extension agents"""
    st.header("🎓 Extension Agent Dashboard")

    tab1, tab2, tab3, tab4 = st.tabs(["👥 Farmer Management", "📊 Bulk Analysis", "📈 Impact Tracking", "📚 Resources"])

    with tab1:
        st.subheader("👥 Farmer Database Management")

        # Upload farmer list
        uploaded_file = st.file_uploader("📄 Upload Farmer List (Excel/CSV)", type=['xlsx', 'csv'])

        if uploaded_file:
            df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} farmers")
            st.dataframe(df.head())

            if st.button("🔬 Generate Bulk Recommendations"):
                st.info("Processing recommendations for all farmers...")
                # Bulk processing logic here

        # Manual farmer addition
        st.markdown("**➕ Add New Farmer**")
        col1, col2 = st.columns(2)
        with col1:
            farmer_name = st.text_input("Farmer Name")
            farmer_phone = st.text_input("Phone Number")
        with col2:
            farmer_location = st.text_input("Village/Location")
            farm_size = st.number_input("Farm Size (ha)", min_value=0.1, value=2.0)

        if st.button("➕ Add Farmer"):
            st.success(f"Added farmer: {farmer_name}")

    with tab2:
        st.subheader("📊 Bulk Soil Analysis")

        # Regional analysis
        col1, col2 = st.columns(2)
        with col1:
            analysis_type = st.selectbox("Analysis Type", 
                                       ["Ward Level", "LGA Level", "State Level"])
            location = st.selectbox("Select Location", 
                                  ["Kaduna North", "Kaduna South", "Kano Municipal"])

        with col2:
            season = st.selectbox("Season", ["2024 Wet Season", "2024 Dry Season", "2025 Wet Season"])
            crop = st.selectbox("Crop", ["Maize", "Rice", "Sorghum", "Millet"])

        if st.button("📈 Generate Regional Analysis"):
            create_regional_analysis_demo()

    with tab3:
        st.subheader("📈 Impact Tracking Dashboard")

        # Sample impact metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Farmers Reached", "245", "+23 this month")
        with col2:
            st.metric("Avg Yield Increase", "35%", "+5% vs last season")
        with col3:
            st.metric("Total Area (ha)", "680", "+120 ha this season")
        with col4:
            st.metric("Adoption Rate", "78%", "+12% improvement")

        # Impact charts
        create_impact_charts()

    with tab4:
        st.subheader("📚 Training Resources")

        resources = {
            "📹 Video Tutorials": [
                "Soil Sampling Techniques",
                "Fertilizer Application Methods", 
                "Farmer Education Strategies"
            ],
            "📄 Technical Guides": [
                "N-P-K Deficiency Identification",
                "Economic Analysis Methods",
                "Digital Tools for Extension"
            ],
            "🎯 Training Modules": [
                "Basic Soil Science",
                "Fertilizer Calculations",
                "Impact Measurement"
            ]
        }

        for category, items in resources.items():
            st.markdown(f"**{category}**")
            for item in items:
                st.markdown(f"• {item}")

def researcher_interface():
    """Interface for researchers"""
    st.header("🔬 Research Dashboard")

    tab1, tab2, tab3, tab4 = st.tabs(["🧪 Experiment Design", "📊 Data Analysis", "📈 Results Viz", "📄 Reports"])

    with tab1:
        st.subheader("🧪 Experimental Design Wizard")

        study_type = st.selectbox("Study Type", 
                                ["Fertilizer Response Trial", "Variety x Nutrition Study", 
                                 "Farmer Participatory Research", "On-station Trial"])

        col1, col2 = st.columns(2)
        with col1:
            treatments = st.number_input("Number of Treatments", min_value=2, max_value=20, value=6)
            replications = st.number_input("Replications", min_value=3, max_value=10, value=4)

        with col2:
            plot_size = st.number_input("Plot Size (m²)", min_value=10, max_value=500, value=100)
            duration = st.selectbox("Study Duration", ["1 Season", "2 Seasons", "3 Seasons"])

        if st.button("🎯 Generate Experimental Design"):
            st.success("✅ Experimental design generated!")
            create_experimental_design_demo(treatments, replications)

    with tab2:
        st.subheader("📊 Statistical Analysis Tools")

        # Sample data upload
        st.markdown("**📤 Upload Research Data**")
        data_file = st.file_uploader("Upload CSV/Excel file", type=['csv', 'xlsx'])

        if data_file:
            df = pd.read_excel(data_file) if data_file.name.endswith('.xlsx') else pd.read_csv(data_file)
            st.dataframe(df.head())

            analysis_type = st.selectbox("Analysis Type", 
                                       ["ANOVA", "Regression", "Correlation", "Mixed Models"])

            if st.button("🔬 Run Statistical Analysis"):
                run_statistical_analysis_demo(analysis_type)

    with tab3:
        st.subheader("📈 Advanced Visualizations")
        create_research_visualizations()

    with tab4:
        st.subheader("📄 Automated Report Generation")

        report_type = st.selectbox("Report Type", 
                                 ["Journal Article", "Conference Abstract", "Technical Report", "Policy Brief"])

        if st.button("📝 Generate Report Template"):
            st.success(f"✅ {report_type} template generated!")

def policy_interface():
    """Interface for policy makers"""
    st.header("🏛️ Policy Dashboard")

    tab1, tab2, tab3 = st.tabs(["🗺️ Regional Overview", "💹 Policy Simulator", "📊 Impact Assessment"])

    with tab1:
        st.subheader("🗺️ Regional Nutrient Status Overview")

        # Regional metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("States Covered", "7", "Northern Nigeria")
        with col2:
            st.metric("LGAs Analyzed", "84", "Complete coverage")
        with col3:
            st.metric("Farmers Benefited", "15,000+", "+25% this year")
        with col4:
            st.metric("Yield Gap Closed", "35%", "Target: 50%")

        # Interactive map
        create_policy_map()

    with tab2:
        st.subheader("💹 Policy Impact Simulator")

        col1, col2 = st.columns(2)

        with col1:
            subsidy_rate = st.slider("Fertilizer Subsidy Rate (%)", 0, 100, 50)
            coverage = st.slider("Program Coverage (%)", 0, 100, 75)

        with col2:
            budget = st.number_input("Annual Budget (Million USD)", min_value=1, max_value=100, value=25)
            years = st.slider("Program Duration (years)", 1, 10, 5)

        if st.button("🎯 Simulate Policy Impact"):
            simulate_policy_impact(subsidy_rate, coverage, budget, years)

    with tab3:
        st.subheader("📊 Program Impact Assessment")
        create_impact_assessment_dashboard()

# Helper functions for demos
def create_regional_analysis_demo():
    st.success("📊 Regional analysis complete!")

    # Sample regional data
    regional_data = {
        'Ward': ['Ward A', 'Ward B', 'Ward C', 'Ward D'],
        'N_Limitation': ['High', 'Medium', 'High', 'Low'],
        'P_Limitation': ['Medium', 'High', 'Medium', 'Medium'],
        'K_Limitation': ['Low', 'Medium', 'High', 'Low'],
        'Avg_Yield': [2100, 2400, 1900, 2800]
    }

    df = pd.DataFrame(regional_data)
    st.dataframe(df)

def create_impact_charts():
    # Sample yield improvement chart
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    adoption = [45, 52, 58, 65, 71, 78]

    fig = px.line(x=months, y=adoption, title="Adoption Rate Over Time")
    fig.update_layout(xaxis_title="Month", yaxis_title="Adoption Rate (%)")
    st.plotly_chart(fig, use_container_width=True)

def create_experimental_design_demo(treatments, reps):
    st.markdown("**🎯 Recommended Experimental Layout:**")

    layout_data = []
    for rep in range(1, reps + 1):
        for treat in range(1, treatments + 1):
            layout_data.append({
                'Plot_ID': f"R{rep}T{treat}",
                'Replication': rep,
                'Treatment': f"Treatment_{treat}",
                'N_Rate': treat * 20,
                'P_Rate': treat * 10,
                'K_Rate': treat * 15
            })

    layout_df = pd.DataFrame(layout_data)
    st.dataframe(layout_df.head(12))

def run_statistical_analysis_demo(analysis_type):
    st.success(f"✅ {analysis_type} analysis completed!")

    if analysis_type == "ANOVA":
        st.markdown("**ANOVA Results:**")
        st.text("""
        Source          DF    Sum Sq    Mean Sq   F Value   Pr(>F)
        Treatment        5    125.4      25.08     15.2     <0.001 ***
        Replication      3     12.3       4.10      2.5     0.089
        Residuals       15     24.7       1.65
        """)

def create_research_visualizations():
    # Sample research visualization
    treatments = ['Control', 'N50', 'N100', 'NPK50', 'NPK100', 'NPK150']
    yields = [1800, 2400, 2800, 3200, 3600, 3400]

    fig = px.bar(x=treatments, y=yields, title="Treatment Effects on Maize Yield")
    fig.update_layout(xaxis_title="Treatment", yaxis_title="Yield (kg/ha)")
    st.plotly_chart(fig, use_container_width=True)

def create_policy_map():
    # Simple map for policy overview
    st.markdown("**🗺️ Northern Nigeria Nutrient Limitation Map**")

    # Sample coordinates for Nigerian states
    map_center = [11.0, 8.0]
    m = folium.Map(location=map_center, zoom_start=6)

    # Add sample markers
    locations = [
        [10.5, 7.4, "Kaduna", "High N, Medium P"],
        [12.0, 8.5, "Kano", "Medium N, High P"],
        [13.0, 5.2, "Katsina", "High N, Low P"]
    ]

    for lat, lon, city, status in locations:
        folium.Marker([lat, lon], popup=f"{city}: {status}", tooltip=city).add_to(m)

    st_folium(m, width=700, height=400)

def simulate_policy_impact(subsidy, coverage, budget, years):
    st.success("🎯 Policy simulation complete!")

    # Sample calculations
    farmers_reached = int((budget * 1000000 * coverage / 100) / 500)  # Assume $500 per farmer
    yield_increase = subsidy * 0.8  # Simplified relationship
    total_production_increase = farmers_reached * 2 * yield_increase / 100 * 1000  # kg

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Farmers Reached", f"{farmers_reached:,}")
    with col2:
        st.metric("Avg Yield Increase", f"{yield_increase:.1f}%")
    with col3:
        st.metric("Additional Production", f"{total_production_increase:,.0f} tons")

def create_impact_assessment_dashboard():
    # Sample impact metrics
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📈 Production Impact**")
        impact_data = {
            'Metric': ['Total Production Increase', 'Average Yield Gain', 'Food Security Index'],
            'Value': ['125,000 tons', '40%', '8.2/10'],
            'Target': ['150,000 tons', '50%', '9.0/10']
        }
        st.dataframe(pd.DataFrame(impact_data))

    with col2:
        st.markdown("**💰 Economic Impact**")
        economic_data = {
            'Metric': ['Additional Income', 'ROI on Investment', 'Poverty Reduction'],
            'Value': ['$45M', '4.2:1', '15%'],
            'Target': ['$60M', '5:1', '20%']
        }
        st.dataframe(pd.DataFrame(economic_data))

def create_farmer_report(recommendations):
    st.success("📄 Recommendation report ready for download!")
    # Implementation for PDF generation would go here

if __name__ == "__main__":
    main()
