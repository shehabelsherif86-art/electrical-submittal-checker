import streamlit as st
import google.generativeai as genai
import tempfile
import os

# إعدادات صفحة الويب
st.set_page_config(page_title="AI Electrical Submittal & Spec Checker", page_icon="⚡", layout="wide")

st.title("⚡ المنصة الذكية لمراجعة العروض الفنية ومطابقة مواصفات مشاريع الكهرباء")
st.markdown("نظام هندسي متكامل لمقارنة مواصفات المشروع الفنية مع العروض المقدمة من الموردين والمقاولين الباطن ل**جميع بنود وأعمال الكهرباء** (كابلات، لوحات، إنارة، قواطع، محولات، إلخ).")

# الشريط الجانبي لإدخال مفتاح الـ API
with st.sidebar:
    st.header("إعدادات النظام")
    api_key = st.text_input("أدخل مفتاح Google AI Studio API Key", type="password")
    st.markdown("---")
    st.info("💡 **طريقة الاستخدام:**\n1. أدخل مفتاح الـ API المجاني.\n2. ارفع مستند مواصفات المشروع (PDF) لأي بند كهربائي.\n3. ارفع العرض الفني/المستند المقدم من المورد (PDF).\n4. اضغط زر تحليل ومقارنة.")

# تقسيم الشاشة لرفع الملفين
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. مواصفات المشروع (Project Specifications)")
    spec_file = st.file_uploader("اختر ملف المواصفات الفنية (PDF)", type=["pdf"], key="spec")

with col2:
    st.subheader("2. العرض الفني للمورد (Vendor Submittal)")
    sub_file = st.file_uploader("اختر ملف العرض الفني للمورد (PDF)", type=["pdf"], key="sub")

# زر بدء التحليل
if st.button("🚀 بدء الفحص والمقارنة الهندسية الشاملة", type="primary"):
    if not api_key:
        st.error("الرجاء إدخال مفتاح الـ API في الشريط الجانبي أولاً.")
    elif not spec_file or not sub_file:
        st.error("الرجاء رفع المستندين (المواصفات والعرض الفني) للمتابعة.")
    else:
        with st.spinner("جاري قراءة المستندات، تحديد البند الكهربائي، ومطابقة المعايير الفنية بالذكاء الاصطناعي..."):
            try:
                # إعداد الاتصال بجيميناي
                genai.configure(api_key=api_key)
                
                # حفظ الملفات المرفوعة مؤقتاً لمعالجتها
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f1:
                    f1.write(spec_file.getbuffer())
                    spec_path = f1.name
                    
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f2:
                    f2.write(sub_file.getbuffer())
                    sub_path = f2.name

                # رفع الملفات إلى خوادم جيميناي المؤقتة
                spec_ref = genai.upload_file(spec_path)
                sub_ref = genai.upload_file(sub_path)

                # استخدام نموذج Gemini 1.5 Flash السريع والقوي
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # صياغة البرومپت الهندسي الشامل والذكي
                prompt = """
                أنت مهندس كهرباء استشاري خبير في مراجعة العروض الفنية واعتماد الموردين والمقاولين في قطاع المقاولات.
                لديك مستندان مرفقان:
                1. مستند مواصفات المشروع الفنية لأعمال الكهرباء.
                2. العرض الفني المقدم من المورد (Vendor Submittal) لأي بند كهربائي (سواء كان كابلات، لوحات توزيع، قواطع، إنارة، محولات، مولدات، أو أنظمة تيار خفيف).
                
                قم بالآتي:
                - أولاً: تعرف بذكاء على "نوع البند الكهربائي" محل المقارنة من المستندات.
                - ثانياً: قم بعمل مطابقة دقيقة واحترافية بين متطلبات المواصفات وما عرضه المورد.
                - ثالثاً: أخرج تقريراً هندسياً منظماً في جدول أو فقرات واضحة يوضح الآتي:
                  1. **البند الكهربائي المدروس:** (تحديد البند مثل: لوحات توزيع رئيسية، كابلات، إضاءة، إلخ).
                  2. **البنود والمواصفات المطابقة (Compliant Items):** العناصر التي تتوافق تماماً مع المواصفة المطلوبة.
                  3. **القصور، الاختلافات أو عدم التطابق (Non-Compliances / Gaps):** أي نقص، اختلاف في الماركات المقترحة، السعة، المعايير القياسية، أو الخامات.
                  4. **التوصية الفنية النهائية (Recommendation):** (قبول - Approved / مرفوض - Rejected / أو طلب توضيح - Revise & Resubmit) مع إبداء السبب الهندسي باختصار.
                """

                # إرسال الملفات والبرومپت للنموذج
                response = model.generate_content([spec_ref, sub_ref, prompt])
                
                # عرض النتيجة على الموقع
                st.success("✅ تم الانتهاء من التحليل الهندسي وإعداد التقرير بنجاح!")
                st.markdown("### 📊 التقرير الفني والمقارنة:")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة: {e}")