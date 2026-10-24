import streamlit as st
import google.generativeai as genai
import tempfile
import os

# إعداد صفحة ستريمليت
st.set_page_config(
    page_title="المنصة الذكية لمراجعة العروض الفنية ومطابقة مواصفات مشاريع الكهرباء",
    layout="wide"
)

# القائمة الجانبية لإدخال مفتاح الـ API
st.sidebar.markdown("### إعدادات النظام")
api_key = st.sidebar.text_input("Google AI Studio API Key", type="password")

st.sidebar.markdown("""
---
### 💡 طريقة الاستخدام:
1. أدخل مفتاح الـ API الجديد.
2. ارفع مستند مواصفات المشروع (PDF) لأي بند كهربائي.
3. ارفع العرض الفني/المستند المقدم من المورد (PDF).
4. اضغط زر تحليل ومقارنة.
""")

# العنوان الرئيسي
st.markdown("""
# ⚡ المنصة الذكية لمراجعة العروض الفنية ومطابقة مواصفات مشاريع الكهرباء
نظام هندسي متكامل لمقارنة مواصفات المشروع الفنية مع العروض المقدمة من الموردين والمقاولين الباطن لجميع بنود وأعمال الكهرباء (كابلات، لوحات، إنارة، قواطع، محولات، إلخ).
""")

# تقسيم الشاشة لرفع الملفات
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1. مواصفات المشروع (Project Specifications)")
    spec_file = st.file_uploader("اختر ملف المواصفات الفنية (PDF)", type=["pdf"], key="spec")

with col2:
    st.markdown("### 2. العرض الفني للمورد (Vendor Submittal)")
    sub_file = st.file_uploader("اختر ملف العرض الفني للمورد (PDF)", type=["pdf"], key="sub")

# زر بدء الفحص
if st.button("🚀 بدء الفحص والمقارنة الهندسية الشاملة", type="primary"):
    if not api_key:
        st.error("الرجاء إدخال مفتاح Google AI Studio API Key في القائمة الجانبية أولاً.")
    elif not spec_file or not sub_file:
        st.warning("الرجاء رفع ملف مواصفات المشروع وملف العرض الفني للمورد معاً.")
    else:
        try:
            # تهيئة المفتاح بالطريقة المتوافقة مع المفاتيح الحديثة
            genai.configure(api_key=api_key.strip())
            
            with st.spinner("جاري معالجة الملفات وتحليل المطابقة الهندسية بواسطة الذكاء الاصطناعي..."):
                # حفظ الملفات مؤقتاً
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f1:
                    f1.write(spec_file.getbuffer())
                    spec_path = f1.name

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f2:
                    f2.write(sub_file.getbuffer())
                    sub_path = f2.name

                # رفع الملفات إلى خوادم جيميني المؤقتة
                spec_ref = genai.upload_file(spec_path)
                sub_ref = genai.upload_file(sub_path)

                # استخدام نموذج Gemini 1.5 Flash المحدث
                model = genai.GenerativeModel("gemini-1.5-flash")

                # صياغة البرومبت الهندسي الشامل والذكي
                prompt = """
                أنت استشاري هندسي كهربائي محترف وخبير في مراجعة العروض الفنية (Technical Submittals) ومطابقة المواصفات القياسية لمشاريع البنية التحتية والمنشآت.
                قم بمقارنة مستند "مواصفات المشروع" مع "العرض الفني المقدم من المورد" بدقة هندسية تامة.
                
                قم بإعداد تقرير هندسي احترافي باللغة العربية يتضمن العناصر التالية:
                1. **ملخص تنفيذي:** نظرة عامة عن البند محل المقارنة (كابلات، لوحات، محولات، قواطع، إنارة، إلخ).
                2. **جدول المطابقة الفنية (Technical Compliance Table):** جدول يوضح (المواصفات المطلوبة، المواصفات المقدمة من المورد، حالة المطابقة: مطابق / غير مطابق / مطابقة بشروط).
                3. **الانحرافات والاختلافات الجوهرية (Deviations & Discrepancies):** رصد أي قصور أو فروق فنية عن المواصفات الاستشارية.
                4. **التوصية النهائية والقرار الهندسي:** (قبول، قبول مع ملاحظات، أو رفض مع إبداء الأسباب الهندسية).
                """

                response = model.generate_content([spec_ref, sub_ref, prompt])

                st.success("تم إتمام الفحص الهندسي بنجاح!")
                st.markdown("### 📋 التقرير الهندسي للمقارنة والمطابقة:")
                st.markdown(response.text)

                # تنظيف الملفات المؤقتة
                os.unlink(spec_path)
                os.unlink(sub_path)

        except Exception as e:
            st.error(f"حدث خطأ أثناء المعالجة: {e}")
