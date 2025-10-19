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

def get_achievement_badges(level):
    """Get achievement badges based on level"""
    badges = []
    
    if level >= 1:
        badges.append({"name": "آغازگر", "emoji": "🌟", "description": "رسیدن به سطح ۱"})
    if level >= 3:
        badges.append({"name": "پیشرو", "emoji": "⭐", "description": "رسیدن به سطح ۳"})
    if level >= 5:
        badges.append({"name": "فعال", "emoji": "✨", "description": "رسیدن به سطح ۵"})
    if level >= 10:
        badges.append({"name": "نمونه", "emoji": "🏆", "description": "رسیدن به سطح ۱۰"})
    if level >= 15:
        badges.append({"name": "ستاره", "emoji": "💎", "description": "رسیدن به سطح ۱۵"})
    if level >= 20:
        badges.append({"name": "قهرمان", "emoji": "👑", "description": "رسیدن به سطح ۲۰"})
    
    return badges

def generate_certificate_html(member_name, level, points, date):
    """Generate HTML certificate for a member"""
    return f"""
    <div style="
        width: 800px;
        height: 600px;
        border: 10px solid #1f5f3f;
        border-radius: 20px;
        background: linear-gradient(135deg, #f0f8f0, #ffffff);
        padding: 40px;
        text-align: center;
        font-family: 'Tahoma', sans-serif;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin: 20px auto;
    ">
        <div style="margin-bottom: 30px;">
            <svg width="100" height="100" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="10" y="60" width="80" height="30" fill="#1f5f3f" rx="2"/>
                <rect x="20" y="50" width="10" height="30" fill="#2d8a4f"/>
                <rect x="70" y="50" width="10" height="30" fill="#2d8a4f"/>
                <circle cx="25" cy="45" r="8" fill="#1f5f3f"/>
                <circle cx="75" cy="45" r="8" fill="#1f5f3f"/>
                <rect x="24" y="37" width="2" height="15" fill="#2d8a4f"/>
                <rect x="74" y="37" width="2" height="15" fill="#2d8a4f"/>
                <path d="M30 60 L50 40 L70 60" fill="#1f5f3f"/>
                <rect x="45" y="65" width="10" height="20" fill="#8B4513"/>
                <circle cx="50" cy="30" r="12" fill="#FFD700"/>
                <path d="M50 18 L52 26 L50 30 L48 26 Z" fill="#FFD700"/>
            </svg>
        </div>
        
        <h1 style="color: #1f5f3f; font-size: 48px; margin: 20px 0; direction: rtl;">گواهینامه تقدیر</h1>
        
        <div style="margin: 40px 0; direction: rtl;">
            <p style="font-size: 24px; color: #2c3e2c; margin: 20px 0;">
                این گواهینامه به
            </p>
            <h2 style="color: #1f5f3f; font-size: 40px; margin: 20px 0; font-weight: bold;">
                {member_name}
            </h2>
            <p style="font-size: 24px; color: #2c3e2c; margin: 20px 0;">
                اهدا می‌گردد
            </p>
        </div>
        
        <div style="background: #e8f5e8; padding: 20px; border-radius: 10px; margin: 30px 0; direction: rtl;">
            <p style="font-size: 20px; color: #1f5f3f; margin: 10px 0;">
                🏆 <strong>سطح {level}</strong> - <strong>{points} امتیاز</strong>
            </p>
            <p style="font-size: 18px; color: #2d8a4f; margin: 10px 0;">
                به پاس تعهد و فعالیت در گروه مسجدی
            </p>
        </div>
        
        <div style="margin-top: 40px; direction: rtl;">
            <p style="font-size: 16px; color: #666;">
                تاریخ صدور: {date}
            </p>
        </div>
        
        <div style="margin-top: 30px;">
            <div style="display: inline-block; border-top: 2px solid #1f5f3f; padding-top: 10px; width: 200px;">
                <p style="color: #1f5f3f; font-size: 16px;">مسئول گروه</p>
            </div>
        </div>
    </div>
    """

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

def save_uploaded_photo(uploaded_file, member_index):
    """Save uploaded photo and return the file path"""
    try:
        if uploaded_file is not None:
            # Create photos directory if it doesn't exist
            photos_dir = "member_photos"
            if not os.path.exists(photos_dir):
                os.makedirs(photos_dir)
            
            # Generate unique filename
            file_extension = uploaded_file.name.split('.')[-1]
            file_path = os.path.join(photos_dir, f"member_{member_index}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}")
            
            # Save the file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            return file_path
        return None
    except Exception as e:
        print(f"Error saving photo: {e}")
        return None

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
    
    # Photo upload
    uploaded_photo = st.file_uploader("تصویر عضو (اختیاری)", type=['png', 'jpg', 'jpeg'], key="new_photo")
    
    if st.button("افزودن عضو", type="primary"):
        if first_name and last_name:
            # Get current member count for photo naming
            member_count = data_manager.get_member_count()
            
            # Save photo if uploaded
            photo_path = None
            if uploaded_photo:
                photo_path = save_uploaded_photo(uploaded_photo, member_count)
            
            member_data = {
                "first_name": first_name,
                "last_name": last_name,
                "birth_date": birth_date.strftime("%Y-%m-%d"),
                "responsibility": responsibility,
                "description": description,
                "points": 0,
                "photo_path": photo_path
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
                # Display current photo if exists
                if member.get('photo_path') and os.path.exists(member['photo_path']):
                    col_photo, col_info = st.columns([1, 3])
                    with col_photo:
                        st.image(member['photo_path'], width=150, caption="تصویر فعلی")
                
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
                
                # Photo upload for editing
                new_photo = st.file_uploader("تغییر تصویر (اختیاری)", type=['png', 'jpg', 'jpeg'], key=f"edit_photo_{idx}")
                
                with col3:
                    if st.button("ویرایش", key=f"edit_{idx}", type="secondary"):
                        # Save new photo if uploaded
                        photo_path = member.get('photo_path')
                        if new_photo:
                            photo_path = save_uploaded_photo(new_photo, idx)
                        
                        updated_member = {
                            "first_name": new_first_name,
                            "last_name": new_last_name,
                            "birth_date": new_birth_date.strftime("%Y-%m-%d"),
                            "responsibility": new_responsibility,
                            "description": new_description,
                            "points": member.get('points', 0),
                            "photo_path": photo_path
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
            
            # Create columns - add photo column if photo exists
            if member.get('photo_path') and os.path.exists(member['photo_path']):
                col_photo, col1, col2, col3, col4 = st.columns([1, 2, 3, 1, 1])
                with col_photo:
                    st.image(member['photo_path'], width=100)
            else:
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
                
                # Display achievement badges
                badges = get_achievement_badges(level)
                if badges:
                    badge_text = " ".join([f"{badge['emoji']}" for badge in badges])
                    st.markdown(f"**نشان‌ها:** {badge_text}")
            
            with col2:
                st.write("**نوار پیشرفت:**")
                current_level = render_score_bar(current_points, points_for_next)
            
            with col3:
                if st.button("➕", key=f"add_{idx}", help="افزایش امتیاز"):
                    data_manager.update_member_points(idx, current_points + 1, "افزایش یک امتیاز")
                    st.rerun()
                
                if st.button("⬆️", key=f"add5_{idx}", help="افزایش 5 امتیاز"):
                    data_manager.update_member_points(idx, current_points + 5, "افزایش 5 امتیاز")
                    st.rerun()
            
            with col4:
                if st.button("➖", key=f"sub_{idx}", help="کاهش امتیاز"):
                    new_points = max(0, current_points - 1)
                    data_manager.update_member_points(idx, new_points, "کاهش یک امتیاز")
                    st.rerun()
                
                if st.button("⬇️", key=f"sub5_{idx}", help="کاهش 5 امتیاز"):
                    new_points = max(0, current_points - 5)
                    data_manager.update_member_points(idx, new_points, "کاهش 5 امتیاز")
                    st.rerun()
            
            # Custom point adjustment and history
            with st.expander("تنظیم دستی امتیاز و تاریخچه"):
                col_adjust, col_reason = st.columns([2, 3])
                
                with col_adjust:
                    new_points = st.number_input(
                        "امتیاز جدید:",
                        min_value=0,
                        value=current_points,
                        key=f"custom_points_{idx}"
                    )
                
                with col_reason:
                    reason = st.text_input(
                        "دلیل تغییر:",
                        key=f"reason_{idx}",
                        placeholder="مثلاً: برگزاری نماز جماعت"
                    )
                
                if st.button("اعمال تغییر", key=f"apply_custom_{idx}"):
                    data_manager.update_member_points(idx, new_points, reason if reason else "تنظیم دستی")
                    st.rerun()
                
                # Display history
                st.divider()
                st.write("**📜 تاریخچه امتیازات:**")
                
                history = data_manager.get_member_history(idx)
                if history:
                    # Show last 10 entries
                    for entry in reversed(history[-10:]):
                        change_symbol = "📈" if entry['change'] > 0 else "📉" if entry['change'] < 0 else "➡️"
                        change_text = f"+{entry['change']}" if entry['change'] > 0 else str(entry['change'])
                        
                        st.markdown(f"""
                        <div style="background: #f0f8f0; padding: 8px; margin: 5px 0; border-radius: 5px; border-right: 3px solid #1f5f3f;">
                            {change_symbol} <strong>{change_text}</strong> امتیاز 
                            ({entry['old_points']} ← {entry['new_points']})
                            <br>
                            <small>📅 {entry['timestamp']}</small>
                            <br>
                            <small>💬 {entry['reason']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("هنوز تاریخچه‌ای ثبت نشده است.")
                
                # Certificate section
                if level >= 1:
                    st.divider()
                    st.write("**🏅 گواهینامه و نشان‌ها:**")
                    
                    # Display all earned badges
                    badges = get_achievement_badges(level)
                    if badges:
                        cols = st.columns(min(len(badges), 4))
                        for i, badge in enumerate(badges):
                            with cols[i % len(cols)]:
                                st.markdown(f"""
                                <div style="background: #e8f5e8; padding: 10px; border-radius: 10px; text-align: center; margin: 5px;">
                                    <div style="font-size: 40px;">{badge['emoji']}</div>
                                    <div style="font-size: 14px; font-weight: bold; color: #1f5f3f;">{badge['name']}</div>
                                    <div style="font-size: 11px; color: #666;">{badge['description']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Certificate generation button
                    if st.button("📜 نمایش گواهینامه", key=f"cert_{idx}"):
                        member_name = f"{member['first_name']} {member['last_name']}"
                        cert_date = datetime.now().strftime("%Y/%m/%d")
                        certificate_html = generate_certificate_html(member_name, level, current_points, cert_date)
                        st.markdown(certificate_html, unsafe_allow_html=True)
                        st.info("💡 برای چاپ یا ذخیره، از دکمه Print مرورگر استفاده کنید (Ctrl+P یا Cmd+P)")
            
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
