import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import os
from data_manager import DataManager

# Configure page
st.set_page_config(
    page_title="سیستم مدیریت اعضای مسجد",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data manager
data_manager = DataManager()

# Custom CSS for mosque theme
st.markdown("""
<style>
.mosque-header {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #1f5f3f, #2d8a4f);
    color: white;
    border-radius: 10px;
    margin-bottom: 20px;
}

.member-card {
    background: white;
    padding: 15px;
    border-radius: 10px;
    border: 2px solid #1f5f3f;
    margin: 10px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.score-bar {
    height: 30px;
    border-radius: 15px;
    border: 2px solid #1f5f3f;
    overflow: hidden;
    margin: 10px 0;
}

.level-badge {
    background: #1f5f3f;
    color: white;
    padding: 5px 15px;
    border-radius: 20px;
    font-weight: bold;
    display: inline-block;
    margin: 5px;
}

.rtl {
    direction: rtl;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

def get_level_info(points):
    """Calculate level and progress based on points"""
    if points < 20:
        return 0, points, 20
    else:
        level = 1 + (points - 20) // 30
        points_in_level = (points - 20) % 30
        points_for_next = 30
        return level, points_in_level, points_for_next

def get_score_bar_color(progress_percent):
    """Generate color based on progress percentage"""
    if progress_percent < 25:
        return "#ff4444"  # Red
    elif progress_percent < 50:
        return "#ff8800"  # Orange
    elif progress_percent < 75:
        return "#ffdd00"  # Yellow
    else:
        return "#44ff44"  # Green

def render_score_bar(points, max_points_for_level):
    """Render animated score bar"""
    level, points_in_level, points_for_next = get_level_info(points)
    progress_percent = (points_in_level / points_for_next) * 100
    color = get_score_bar_color(progress_percent)
    
    st.markdown(f"""
    <div class="score-bar">
        <div style="
            width: {progress_percent}%;
            height: 100%;
            background: {color};
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        ">
            {points_in_level}/{points_for_next}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    return level

def member_management_page():
    """Member management page"""
    st.markdown("""
    <div class="mosque-header">
        <h1>🕌 سیستم مدیریت اعضای مسجد</h1>
        <p>مدیریت اطلاعات بچه‌های گروه مسجدی</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="rtl">', unsafe_allow_html=True)
    
    # Add new member section
    st.subheader("➕ افزودن عضو جدید")
    
    col1, col2 = st.columns(2)
    
    with col1:
        first_name = st.text_input("نام", key="first_name")
        birth_date = st.date_input("تاریخ تولد", key="birth_date", max_value=date.today())
        
    with col2:
        last_name = st.text_input("نام خانوادگی", key="last_name")
        responsibility = st.text_input("مسئولیت", key="responsibility")
    
    description = st.text_area("توضیحات", key="description")
    
    if st.button("افزودن عضو", type="primary"):
        if first_name and last_name:
            member_data = {
                "first_name": first_name,
                "last_name": last_name,
                "birth_date": birth_date.strftime("%Y-%m-%d"),
                "responsibility": responsibility,
                "description": description,
                "points": 0
            }
            
            if data_manager.add_member(member_data):
                st.success("✅ عضو با موفقیت اضافه شد!")
                st.rerun()
            else:
                st.error("❌ خطا در افزودن عضو!")
        else:
            st.error("⚠️ لطفاً نام و نام خانوادگی را وارد کنید!")
    
    st.divider()
    
    # Display existing members
    st.subheader("📋 لیست اعضای فعلی")
    
    members = data_manager.get_all_members()
    
    if not members:
        st.info("هیچ عضوی ثبت نشده است.")
    else:
        for idx, member in enumerate(members):
            with st.expander(f"👤 {member['first_name']} {member['last_name']}"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    new_first_name = st.text_input("نام", value=member['first_name'], key=f"edit_fname_{idx}")
                    new_birth_date = st.date_input("تاریخ تولد", 
                                                 value=datetime.strptime(member['birth_date'], "%Y-%m-%d").date(),
                                                 key=f"edit_bdate_{idx}",
                                                 max_value=date.today())
                
                with col2:
                    new_last_name = st.text_input("نام خانوادگی", value=member['last_name'], key=f"edit_lname_{idx}")
                    new_responsibility = st.text_input("مسئولیت", value=member.get('responsibility', ''), key=f"edit_resp_{idx}")
                
                new_description = st.text_area("توضیحات", value=member.get('description', ''), key=f"edit_desc_{idx}")
                
                with col3:
                    if st.button("ویرایش", key=f"edit_{idx}", type="secondary"):
                        updated_member = {
                            "first_name": new_first_name,
                            "last_name": new_last_name,
                            "birth_date": new_birth_date.strftime("%Y-%m-%d"),
                            "responsibility": new_responsibility,
                            "description": new_description,
                            "points": member.get('points', 0)
                        }
                        
                        if data_manager.update_member(idx, updated_member):
                            st.success("✅ اطلاعات به‌روزرسانی شد!")
                            st.rerun()
                        else:
                            st.error("❌ خطا در به‌روزرسانی!")
                    
                    if st.button("حذف", key=f"delete_{idx}", type="secondary"):
                        if data_manager.delete_member(idx):
                            st.success("✅ عضو حذف شد!")
                            st.rerun()
                        else:
                            st.error("❌ خطا در حذف!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def scoring_page():
    """Scoring page"""
    st.markdown("""
    <div class="mosque-header">
        <h1>🏆 سیستم امتیازدهی</h1>
        <p>مدیریت امتیازات اعضای گروه</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="rtl">', unsafe_allow_html=True)
    
    members = data_manager.get_all_members()
    
    if not members:
        st.info("هیچ عضوی برای امتیازدهی یافت نشد. ابتدا اعضا را در صفحه مدیریت اعضا اضافه کنید.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Display members with scoring interface
    for idx, member in enumerate(members):
        with st.container():
            st.markdown(f"""
            <div class="member-card">
                <h3>👤 {member['first_name']} {member['last_name']}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns([2, 3, 1, 1])
            
            with col1:
                current_points = member.get('points', 0)
                level, points_in_level, points_for_next = get_level_info(current_points)
                
                st.markdown(f"""
                <div class="level-badge">
                    سطح {level}
                </div>
                """, unsafe_allow_html=True)
                
                st.write(f"**مجموع امتیازات:** {current_points}")
            
            with col2:
                st.write("**نوار پیشرفت:**")
                current_level = render_score_bar(current_points, points_for_next)
            
            with col3:
                if st.button("➕", key=f"add_{idx}", help="افزایش امتیاز"):
                    data_manager.update_member_points(idx, current_points + 1)
                    st.rerun()
                
                if st.button("⬆️", key=f"add5_{idx}", help="افزایش 5 امتیاز"):
                    data_manager.update_member_points(idx, current_points + 5)
                    st.rerun()
            
            with col4:
                if st.button("➖", key=f"sub_{idx}", help="کاهش امتیاز"):
                    new_points = max(0, current_points - 1)
                    data_manager.update_member_points(idx, new_points)
                    st.rerun()
                
                if st.button("⬇️", key=f"sub5_{idx}", help="کاهش 5 امتیاز"):
                    new_points = max(0, current_points - 5)
                    data_manager.update_member_points(idx, new_points)
                    st.rerun()
            
            # Custom point adjustment
            with st.expander("تنظیم دستی امتیاز"):
                new_points = st.number_input(
                    "امتیاز جدید:",
                    min_value=0,
                    value=current_points,
                    key=f"custom_points_{idx}"
                )
                
                if st.button("اعمال", key=f"apply_custom_{idx}"):
                    data_manager.update_member_points(idx, new_points)
                    st.rerun()
            
            st.divider()
    
    # Leaderboard
    st.subheader("🥇 جدول رتبه‌بندی")
    
    # Sort members by points
    sorted_members = sorted(members, key=lambda x: x.get('points', 0), reverse=True)
    
    leaderboard_data = []
    for rank, member in enumerate(sorted_members, 1):
        points = member.get('points', 0)
        level, _, _ = get_level_info(points)
        
        leaderboard_data.append({
            "رتبه": rank,
            "نام": f"{member['first_name']} {member['last_name']}",
            "امتیاز": points,
            "سطح": level
        })
    
    df = pd.DataFrame(leaderboard_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application"""
    # Sidebar navigation
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h2>🕌 منوی اصلی</h2>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.selectbox(
        "انتخاب صفحه:",
        ["مدیریت اعضا", "امتیازدهی"],
        index=0
    )
    
    # Display mosque icon in sidebar
    st.sidebar.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <svg width="100" height="100" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="10" y="60" width="80" height="30" fill="#1f5f3f" rx="2"/>
            <rect x="20" y="50" width="10" height="30" fill="#2d8a4f"/>
            <rect x="70" y="50" width="10" height="30" fill="#2d8a4f"/>
            <circle cx="25" cy="45" r="8" fill="#1f5f3f"/>
            <circle cx="75" cy="45" r="8" fill="#1f5f3f"/>
            <rect x="25" y="37" width="2" height="15" fill="#2d8a4f"/>
            <rect x="75" y="37" width="2" height="15" fill="#2d8a4f"/>
            <path d="M30 60 L50 40 L70 60" fill="#1f5f3f"/>
            <rect x="45" y="65" width="10" height="20" fill="#8B4513"/>
            <circle cx="50" cy="30" r="12" fill="#FFD700"/>
            <path d="M50 18 L52 26 L50 30 L48 26 Z" fill="#FFD700"/>
        </svg>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **راهنما:**\n\n• در صفحه مدیریت اعضا می‌توانید اعضای جدید اضافه کنید\n• در صفحه امتیازدهی می‌توانید امتیاز اعضا را مدیریت کنید\n• سیستم سطح‌بندی: سطح ۱ در ۲۰ امتیاز، سپس هر ۳۰ امتیاز یک سطح")
    
    # Route to appropriate page
    if page == "مدیریت اعضا":
        member_management_page()
    elif page == "امتیازدهی":
        scoring_page()

if __name__ == "__main__":
    main()
