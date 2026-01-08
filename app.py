import streamlit as st
from rembg import remove
from PIL import Image
import io
import google.generativeai as genai

# --- CẤU HÌNH ---
# Để trống, người dùng sẽ nhập Key trên web để bảo mật
DEFAULT_API_KEY = "" 

def phan_tich_trang_phuc(api_key, image):
    """Gửi ảnh lên Google Gemini để phân tích"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prompt (câu lệnh) gửi cho AI
        response = model.generate_content([
            "Bạn là một chuyên gia thời trang. Hãy nhìn ảnh này và mô tả ngắn gọn: Loại trang phục là gì? Màu sắc? Chất liệu dự đoán? Phong cách (hiện đại, cổ điển, v.v.)? Trả lời bằng tiếng Việt, trình bày gạch đầu dòng.", 
            image
        ])
        return response.text
    except Exception as e:
        return f"⚠️ Lỗi kết nối Google AI: {str(e)}"

def xu_ly_anh(uploaded_file):
    """Đọc file ảnh tải lên"""
    image = Image.open(uploaded_file)
    return image

def main():
    st.set_page_config(page_title="AI Tách Đồ & Stylist", page_icon="👕", layout="wide")
    
    st.title("👕 AI Tách Đồ & Stylist Ảo")
    st.markdown("---")

    # Cột bên trái: Cấu hình và Tải ảnh
    with st.sidebar:
        st.header("⚙️ Cấu hình")
        api_key = st.text_input("Nhập API Key Google AI Studio", type="password")
        st.caption("Truy cập [Google AI Studio](https://aistudio.google.com/) để lấy Key miễn phí.")
        st.divider()
        st.info("💡 Cách dùng:\n1. Nhập API Key\n2. Tải ảnh lên\n3. Bấm nút xử lý")

    # Khu vực chính
    uploaded_file = st.file_uploader("📤 Tải ảnh trang phục lên (JPG, PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        original_image = xu_ly_anh(uploaded_file)
        
        # Chia giao diện thành 2 cột
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📸 Ảnh gốc")
            st.image(original_image, use_container_width=True)

        # Nút bấm xử lý
        if st.button("✨ Tách nền & Phân tích ngay", type="primary"):
            if not api_key:
                st.warning("⚠️ Bạn chưa nhập API Key. Ứng dụng chỉ sẽ Tách nền, không Phân tích được.")
            
            with st.spinner("⏳ Đang xử lý... AI đang làm việc..."):
                # 1. Tách nền
                try:
                    fixed_image = remove(original_image)
                    
                    with col2:
                        st.subheader("🖼️ Đã tách nền")
                        st.image(fixed_image, use_container_width=True)
                        
                        # Tạo nút tải về
                        buf = io.BytesIO()
                        fixed_image.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        st.download_button(
                            label="⬇️ Tải ảnh đã tách (PNG)",
                            data=byte_im,
                            file_name="tach_nen_ai.png",
                            mime="image/png"
                        )
                except Exception as e:
                    st.error(f"Lỗi khi tách nền: {e}")

                # 2. Phân tích bằng Gemini
                if api_key:
                    st.divider()
                    st.subheader("🤖 Chuyên gia AI nhận xét:")
                    description = phan_tich_trang_phuc(api_key, original_image)
                    st.success("Đã phân tích xong!")
                    st.write(description)

if __name__ == "__main__":
    main()