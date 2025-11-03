import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="Ballard District - Teacher Absence Analysis",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #2E86AB;
        margin: 1rem 0;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .chart-title {
        font-size: 1.5rem;
        color: #2E86AB;
        font-weight: bold;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ABCover Logo centered at the top
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("abcover_logo.png", width=400)

# Ballard logo centered under ABCover
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image("ballard_logo.png", width=150)

# Main header centered
st.markdown('<h1 class="main-header" style="color: #2E8B57; text-align: center;">Ballard District - Teacher Absence Analysis Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("📋 Navigation")
page = st.sidebar.selectbox(
    "Choose a section:",
    ["🏠 Executive Summary", "📈 Yearly and Monthly Trends", "👥 Top Teachers", "Teachers category Analysis", 
     "🔥 Teacher Heatmap Analysis", "📊 Absence Type Analysis", "💰 Cost Breakdown", 
     "🛡️ ABCover vs District Coverage"]
)

# Page 1: Executive Summary
if page == "🏠 Executive Summary":
    st.header("🏠 Executive Summary")
    
    # Summary insights
    st.markdown("""
    ### 🎯 Key Insights
    - **Peak Absence Months**: March, November, February show highest costs
    - **Critical Teachers**: 53 teachers with >15 days absence (79.1% of staff)
    - **Year-over-Year Growth**: 90.3% total growth from 2021-2022 to 2024-2025
    - **ABCover Savings**: $89,250 in potential savings (22.7% of total costs)
    - **SICK Absences Dominate**: 81.7% of all absences ($321,256 in costs)
    - **Cost Concentration**: Top 10% of teachers account for 24.6% of total costs
    - **Seasonal Pattern**: November shows significant costs ($42,912)
    - **Consistent High-Risk**: 8 teachers show high absences across multiple years
    """)
    
    # Additional critical findings
    st.subheader("🚨 Critical Findings")
    
    st.markdown("""
    **High-Risk Patterns:**
    - 14 teachers with 50+ days absence (critical risk)
    - 39 teachers with 15-50 days absence (high risk)
    - Monthly volatility: 37.9% (highly unpredictable costs)
    """)

# Page 2: Yearly Trends
elif page == "📈 Yearly and Monthly Trends":
    st.header("📈 Yearly and Monthly Trends")
    
    # Load your yearly trend charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-title">All Teachers Trend</div>', unsafe_allow_html=True)
        st.image("output10.png", use_container_width=True)
    
    with col2:
        st.markdown('<div class="chart-title">Monthly Absence Costs</div>', unsafe_allow_html=True)
        st.image("output-11.png", use_container_width=True)

# Page 3: Top Teachers
elif page == "👥 Top Teachers":
    st.header("👥 Top Teachers Analysis")
    
    # Display the chart first
    st.markdown('<div class="chart-title">Top 10 Teachers by School Year</div>', unsafe_allow_html=True)
    st.image("output7.png", use_container_width=True)
    
    # Load data
    ballard_file = 'Ballard Absences ABCover.xlsx'
    df = pd.read_excel(ballard_file, sheet_name='EMPLOYEE_ACCRUAL_HISTORY')
    
    # Filter for teachers only
    teachers_df_temp = df[
        (df['Job Description'].str.contains('Instruct', case=False, na=False) | 
         df['Job Description'].str.contains('Instr', case=False, na=False)) &
        (~df['Job Description'].str.contains('Instructional Assistant', case=False, na=False))
    ].copy()
    
    # Calculate Manager_Cost
    AVERAGE_REPLACEMENT_COST = 175
    teachers_df_temp['Manager_Cost'] = teachers_df_temp['Used'] * AVERAGE_REPLACEMENT_COST
    
    # Add School Year column
    def get_school_year(date):
        if pd.isna(date):
            return None
        year = date.year
        month = date.month
        if month >= 7:
            return f"{year}-{year+1}"
        else:
            return f"{year-1}-{year}"
    
    teachers_df_temp['School Year'] = teachers_df_temp['From Date'].apply(get_school_year)
    
    # Calculate total absence days for each employee across all years (from original data)
    all_years_data = teachers_df_temp.groupby('Emp #').agg({
        'Used': 'sum',
        'Manager_Cost': 'sum'
    }).reset_index()
    all_years_data.columns = ['Emp #', 'Total Absence Days', 'Total Cost']
    
    # Get top 10
    top_10_all_time = all_years_data.nlargest(10, 'Total Absence Days')
    
    # Calculate ABCover coverage for Top 10
    def calculate_abcover_for_teacher(days, threshold):
        """Calculate ABCover coverage for a teacher"""
        if days <= threshold:
            district_pays = days * AVERAGE_REPLACEMENT_COST
            abcover_pays = 0
        else:
            district_pays = threshold * AVERAGE_REPLACEMENT_COST
            abcover_pays = (days - threshold) * AVERAGE_REPLACEMENT_COST
        total_cost = days * AVERAGE_REPLACEMENT_COST
        district_saves = abcover_pays  # District saves what ABCover pays
        return total_cost, district_pays, abcover_pays, district_saves
    
    # Identify which teachers appear in top 10 across multiple years
    school_years_list = ['2021-2022', '2022-2023', '2023-2024', '2024-2025']
    
    # Calculate total absence days per teacher per school year
    absence_summary_temp = teachers_df_temp.groupby(['School Year', 'Emp #']).agg({
        'Used': 'sum',
        'Manager_Cost': 'sum'
    }).reset_index()
    absence_summary_temp.columns = ['School Year', 'Emp #', 'Total Absence Days', 'Total Cost']
    
    # Get top 10 for each year
    top_teachers_by_year = {}
    for year in school_years_list:
        year_data = absence_summary_temp[absence_summary_temp['School Year'] == year].nlargest(10, 'Total Absence Days')
        top_teachers_by_year[year] = year_data
    
    # Find which teachers appear in multiple years
    teacher_appearances = {}
    for year in school_years_list:
        for emp in top_teachers_by_year[year]['Emp #'].tolist():
            if emp not in teacher_appearances:
                teacher_appearances[emp] = 0
            teacher_appearances[emp] += 1
    
    # Only color teachers who appear more than once
    repeating_teachers = [emp for emp, count in teacher_appearances.items() if count > 1]
    
    # Generate light, pastel colors for repeating teachers only
    light_colors = ['#FFB3BA', '#BAFFC9', '#BAE1FF', '#FFFFBA', '#FFD1DC', '#E0BBE4', '#A8E6CF', '#FFD3A5', 
                    '#FFDFBA', '#B0E0E6', '#F0E68C', '#FFB6C1', '#C5E3F6', '#DDA0DD', '#98FB98', '#F5DEB3',
                    '#FFEFD5', '#E6E6FA', '#F0FFF0', '#FFF0F5', '#FFE4E1', '#F5FFFA', '#FFE4B5', '#FAEBD7']
    
    teacher_colors = {}
    for i, emp in enumerate(repeating_teachers):
        teacher_colors[emp] = light_colors[i % len(light_colors)]
    
    # ABCover Coverage Analysis for Top 10
    st.subheader("💰 ABCover Coverage Analysis for Top 10 Employees")
    
    # Create coverage tables for each threshold
    thresholds = [10, 15, 20]
    threshold_names = ['>10 Days', '>15 Days', '>20 Days']
    
    coverage_tables = []
    for threshold, threshold_name in zip(thresholds, threshold_names):
        coverage_data = []
        for idx, row in top_10_all_time.iterrows():
            emp = row['Emp #']
            days = row['Total Absence Days']
            total_cost, district_pays, abcover_pays, district_saves = calculate_abcover_for_teacher(days, threshold)
            
            coverage_data.append({
                'Emp #': int(emp),
                'Total Days': f"{days:.1f}",
                'Replacement Cost': f"${total_cost:,.0f}",
                'District Pays': f"${district_pays:,.0f}",
                'ABCover Pays': f"${abcover_pays:,.0f}",
                'District Saves': f"${district_saves:,.0f}"
            })
        
        coverage_df = pd.DataFrame(coverage_data)
        coverage_tables.append((threshold_name, coverage_df))
    
    # Display tables with colored rows and legend side by side
    coverage_col1, coverage_col2, coverage_col3 = st.columns(3)
    
    with coverage_col1:
        st.markdown(f"**{coverage_tables[0][0]} Coverage**")
        # Apply coloring
        def highlight_row(row):
            emp = row['Emp #']
            bg_color = teacher_colors.get(emp, '')
            if bg_color:
                return [f'background-color: {bg_color}' for _ in row]
            else:
                return [''] * len(row)
        styled_df = coverage_tables[0][1].style.apply(highlight_row, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    with coverage_col2:
        st.markdown(f"**{coverage_tables[1][0]} Coverage**")
        def highlight_row(row):
            emp = row['Emp #']
            bg_color = teacher_colors.get(emp, '')
            if bg_color:
                return [f'background-color: {bg_color}' for _ in row]
            else:
                return [''] * len(row)
        styled_df = coverage_tables[1][1].style.apply(highlight_row, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    with coverage_col3:
        st.markdown(f"**{coverage_tables[2][0]} Coverage**")
        def highlight_row(row):
            emp = row['Emp #']
            bg_color = teacher_colors.get(emp, '')
            if bg_color:
                return [f'background-color: {bg_color}' for _ in row]
            else:
                return [''] * len(row)
        styled_df = coverage_tables[2][1].style.apply(highlight_row, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # Display color legend for repeating teachers
    if repeating_teachers:
        st.subheader("🎨 Color Legend - Repeating Top 10 Teachers")
        # Group repeating teachers by their rank in top 10 all-time
        legend_data = []
        rank = 1
        for idx, row in top_10_all_time.iterrows():
            emp = row['Emp #']
            if emp in repeating_teachers:
                legend_data.append({
                    'Rank': f"#{rank}",
                    'Emp #': int(emp),
                    'Total Days': f"{row['Total Absence Days']:.1f}",
                    'Color': teacher_colors.get(emp, '')
                })
            rank += 1
        
        if legend_data:
            # Display legend as colored boxes
            num_cols = min(len(legend_data), 5)
            legend_cols = st.columns(num_cols)
            for i, item in enumerate(legend_data):
                with legend_cols[i % num_cols]:
                    st.markdown(f"""
                    <div style="background-color: {item['Color']}; padding: 10px; border-radius: 5px; margin: 5px 0;">
                        <strong>Rank {item['Rank']}</strong><br>
                        Emp #{item['Emp #']}<br>
                        {item['Total Days']} days
                    </div>
                    """, unsafe_allow_html=True)

# Page 4: Teachers category Analysis (Original)
        
elif page == "Teachers category Analysis":
    st.header("📊 Teachers category Analysis")
    
    st.markdown('<div class="chart-title">Teacher Absence Across All Years</div>', unsafe_allow_html=True)
    st.image("output1.png", use_container_width=True)
    
    # Heatmap insights
    st.markdown("""
    ### 🔍 Heatmap Insights
    - **Black borders** indicate teachers with 15-20 days absence
    - **Red cells** show highest absence days (50+ days)
    - **Pattern analysis** reveals consistent high-absence teachers
    - **Risk identification** for ABCover coverage planning
    """)

# Page 5: Teacher Heatmap Analysis (NEW SECTION)
elif page == "🔥 Teacher Heatmap Analysis":
    st.header("🔥 Teacher Heatmap Analysis")
    
    st.markdown('<div class="chart-title">Every Teacher Across All School Years</div>', unsafe_allow_html=True)
    st.image("output_2.png", use_container_width=True)
    
    # Heatmap explanation
    st.markdown("""
    ### 🎨 Color Scale Explanation
    The color scale on the **right side** of the heatmap shows absence days with the following color coding:
    
    - 🔴 **Darkest Red (50+ days)**: Critical absence levels - highest risk teachers
    - 🟠 **Dark Red (45-50 days)**: Very high absence - immediate attention needed  
    - 🟡 **Medium Red (40-45 days)**: High absence - monitor closely
    - 🟢 **Light Red (35-40 days)**: Moderate-high absence - track patterns
    - ⚪ **White/Pale (0-5 days)**: Low absence - healthy attendance
    
    **Key Observations:**
    - Each cell represents one teacher's total absence days for that school year
    - **Employee numbers** are listed on the left (y-axis)
    - **School years** are shown across the bottom (x-axis)
    - **Darker colors** = more absence days = higher substitute costs
    """)
    
    # Additional heatmap insights
    st.markdown("""
    ### 🔍 Pattern Analysis
    - **Consistent High-Absence Teachers**: Look for dark red patterns across multiple years
    - **Seasonal Patterns**: Some teachers show higher absences in specific years
    - **Risk Identification**: Teachers with 15+ days (darker colors) need ABCover coverage
    - **Cost Impact**: Each dark cell represents significant substitute teacher costs
    """)

# Page 6: Absence Type Analysis
elif page == "📊 Absence Type Analysis":
    st.header("📊 Absence Type Analysis")
    
    st.markdown('<div class="chart-title">Absence Type Distribution</div>', unsafe_allow_html=True)
    st.image("type_description_pie_chart.png", use_container_width=True)
    
    # Type analysis insights
    st.markdown("""
    ### 🎯 Key Insights
    - **SICK absences dominate** at 80.3% of all absences (1,380 out of 1,719)
    - **SICK costs are 4.5x higher** than personal absences ($321,256 vs $71,953)
    - **Total absence costs**: $393,209 across all types
    - **ABCover opportunity**: Focus coverage on SICK absences for maximum impact
    """)
    
    # Cost breakdown by type
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="SICK Absences",
            value="1,380",
            delta="80.3%"
        )
        st.metric(
            label="SICK Costs",
            value="$321,256",
            delta="81.7%"
        )
    
    with col2:
        st.metric(
            label="PERSONAL Absences",
            value="339",
            delta="19.7%"
        )
        st.metric(
            label="PERSONAL Costs",
            value="$71,953",
            delta="18.3%"
        )
    
    # Recommendations for ABCover
    st.subheader("💡 ABCover Strategy Recommendations")
    st.markdown("""
    ### 🎯 Focus Areas for ABCover Coverage
    
    1. **Primary Target - SICK Absences**:
       - 80.3% of all absences are SICK-related
       - $321,256 in costs (81.7% of total)
       - Highest impact potential for ABCover coverage
    
    2. **Secondary Target - PERSONAL Absences**:
       - 19.7% of all absences are PERSONAL
       - $71,953 in costs (18.3% of total)
       - Lower volume but still significant cost impact
    
    3. **Coverage Strategy**:
       - Prioritize SICK absence coverage for maximum ROI
       - Consider tiered coverage based on absence type
       - Monitor patterns to predict high-risk periods
    """)

# Page 7: Cost Breakdown
elif page == "💰 Cost Breakdown":
    st.header("👥 Number of Teachers")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="chart-title">Greater than 10 days</div>', unsafe_allow_html=True)
        st.image("output_4.png", use_container_width=True)
    
    with col2:
        st.markdown('<div class="chart-title">Greater than 15 days</div>', unsafe_allow_html=True)
        st.image("output_5.png", use_container_width=True)
    
    with col3:
        st.markdown('<div class="chart-title">Greater than 20 days</div>', unsafe_allow_html=True)
        st.image("output_6.png", use_container_width=True)

# Page 8: ABCover vs District Coverage
elif page == "🛡️ ABCover vs District Coverage":
    st.header("🛡️ ABCover vs District Coverage")
    
    # Display the chart by year
    st.markdown('<div class="chart-title">ABCover Coverage by School Year</div>', unsafe_allow_html=True)
    st.image("abcover_coverage_by_year.png", use_container_width=True)
    
    # Coverage table by threshold (summed across all years)
    st.subheader("📊 ABCover Insurance Coverage Summary (All Years)")
    
    # Sum up all years for each threshold
    # >10 Days
    total_cost_10 = 35086 + 75688 + 64083 + 83673
    district_pays_10 = 17500 + 38500 + 35000 + 47250
    abcover_pays_10 = 17586 + 37188 + 29083 + 36423
    
    # >15 Days
    total_cost_15 = 24274 + 45078 + 43325 + 39582
    district_pays_15 = 13125 + 21000 + 26250 + 18375
    abcover_pays_15 = 11149 + 24078 + 17075 + 21206
    
    # >20 Days
    total_cost_20 = 21474 + 35236 + 37763 + 31057
    district_pays_20 = 14000 + 17500 + 28000 + 14000
    abcover_pays_20 = 7474 + 17736 + 9763 + 17057
    
    # Create summary table
    summary_data = {
        'Threshold': ['>10 Days', '>15 Days', '>20 Days'],
        'Total Cost': [f"${total_cost_10:,}", f"${total_cost_15:,}", f"${total_cost_20:,}"],
        'District Pays': [f"${district_pays_10:,}", f"${district_pays_15:,}", f"${district_pays_20:,}"],
        'ABCover Pays': [f"${abcover_pays_10:,}", f"${abcover_pays_15:,}", f"${abcover_pays_20:,}"],
        'District Savings': [f"${abcover_pays_10:,}", f"${abcover_pays_15:,}", f"${abcover_pays_20:,}"]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    st.markdown("""
    **Note:** District Savings = ABCover Pays - This is the amount the District saves by having ABCover insurance coverage after the deductible threshold.
    """)

# Footer
st.markdown("---")
st.markdown("📊 **Ballard District Teacher Absence Analysis** | Generated with Streamlit | Data: 2021-2025")
