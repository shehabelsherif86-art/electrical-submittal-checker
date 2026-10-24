import streamlit as st
from google import genai
import time
import tempfile
import os

# إعداد صفحة ستريمليت
st.set_page_config(
    page_title="المنصة الذكية لمراجعة العروض الفنية ومطابقة مواصفات مشاريع الكهرباء",
    layout="wide"
)

# ضبط اتجاه النص (عربي + إنجليزي) وشكل الأرقام والجداول
st.markdown("""
<style>
/* الصفحة كلها من اليمين لليسار */
.stApp { direction: rtl; }

/* كل فقرة/عنوان/عنصر قائمة/خلية جدول يحدد اتجاهه حسب أول حرف فيه */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] td,
[data-testid="stMarkdownContainer"] th {
    unicode-bidi: plaintext;
    text-align: start;
}

/* القوائم والجداول تبدأ من اليمين */
[data-testid="stMarkdownContainer"] ul,
[data-testid="stMarkdownContainer"] ol { direction: rtl; }
[data-testid="stMarkdownContainer"] table { direction: rtl; width: 100%; }

/* أي كلمة إنجليزي جوه نص عربي تفضل متماسكة */
[data-testid="stMarkdownContainer"] code {
    direction: ltr;
    unicode-bidi: isolate;
    background: transparent;
    color: inherit;
    padding: 0;
}
</style>
""", unsafe_allow_html=True)

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

# اسم الموديل (لو جوجل قفلته مستقبلاً غيّره من هنا فقط)
MODEL_NAME = "gemini-3.8-flash"


def wait_for_file(client, uploaded):
    """استنى لحد ما الملف المرفوع يبقى جاهز عند جوجل."""
    while uploaded.state.name == "PROCESSING":
        time.sleep(2)
        uploaded = client.files.get(name=uploaded.name)
    if uploaded.state.name == "FAILED":
        raise RuntimeError("فشلت معالجة أحد الملفات عند جوجل. جرّب ملف PDF تاني.")
    return uploaded


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
        spec_path = None
        sub_path = None
        try:
            # تهيئة العميل بالمكتبة الجديدة
            client = genai.Client(api_key=api_key.strip())

            with st.spinner("جاري معالجة الملفات وتحليل المطابقة الهندسية بواسطة الذكاء الاصطناعي..."):
                # حفظ الملفات مؤقتاً
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f1:
                    f1.write(spec_file.getbuffer())
                    spec_path = f1.name

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f2:
                    f2.write(sub_file.getbuffer())
                    sub_path = f2.name

                # رفع الملفات إلى خوادم جيميني المؤقتة
                spec_ref = client.files.upload(file=spec_path)
                sub_ref = client.files.upload(file=sub_path)

                # استنى لحد ما الملفات تبقى جاهزة
                spec_ref = wait_for_file(client, spec_ref)
                sub_ref = wait_for_file(client, sub_ref)

                # صياغة البرومبت الهندسي الشامل والذكي
                prompt = """
                أنت استشاري هندسي كهربائي محترف وخبير في مراجعة العروض الفنية (Technical Submittals) ومطابقة المواصفات القياسية لمشاريع البنية التحتية والمنشآت.
                قم بمقارنة مستند "مواصفات المشروع" مع "العرض الفني المقدم من المورد" بدقة هندسية تامة.

                قم بإعداد تقرير هندسي احترافي باللغة العربية يتضمن العناصر التالية:
                1. **ملخص تنفيذي:** نظرة عامة عن البند محل المقارنة (كابلات، لوحات، محولات، قواطع، إنارة، إلخ).
                2. **جدول المطابقة الفنية (Technical Compliance Table):** جدول يوضح (المواصفات المطلوبة، المواصفات المقدمة من المورد، حالة المطابقة: مطابق / غير مطابق / مطابقة بشروط).
                3. **الانحرافات والاختلافات الجوهرية (Deviations & Discrepancies):** رصد أي قصور أو فروق فنية عن المواصفات الاستشارية.
                4. **التوصية النهائية والقرار الهندسي:** (قبول، قبول مع ملاحظات، أو رفض مع إبداء الأسباب الهندسية).

                قواعد التنسيق (مهمة جداً):
                - اكتب التقرير بالعربية، والمصطلحات الإنجليزية بين قوسين بعد المصطلح العربي، مثال: كابلات أحادية النواة (Single Core).
                - لا تستخدم علامة الدولار ($) ولا صيغ LaTeX نهائياً.
                - لا تستخدم علامات الاقتباس العكسية (`) نهائياً.
                - اكتب كل الأرقام بالأرقام الإنجليزية (0-9).
                - اكتب المقاسات والوحدات كنص عادي، مثال: 4 × 240 مم² أو 4C x 240 mm2، وضع كل مقاس في عمود أو سطر مستقل داخل الجدول بدل دمجه وسط جملة طويلة.
                - لا تكتب جملة عربية طويلة تحتوي على عدة مقاسات وأرقام متتالية؛ استخدم الجدول أو نقاط قصيرة.
                """

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[spec_ref, sub_ref, prompt],
                )

            st.success("تم إتمام الفحص الهندسي بنجاح!")
            st.markdown("### 📋 التقرير الهندسي للمقارنة والمطابقة:")

            # تنظيف النص: علامة $ بتخلي ستريمليت يعرض الأرقام كمعادلات رياضية
            # والـ backticks بتبوّظ ترتيب العربي مع الإنجليزي
            report = response.text.replace("$", "\\$").replace("`", "")
            st.markdown(report)

        except Exception as e:
            st.error(f"حدث خطأ أثناء المعالجة: {e}")

        finally:
            # تنظيف الملفات المؤقتة
            for p in (spec_path, sub_path):
                if p and os.path.exists(p):
                    os.unlink(p)
