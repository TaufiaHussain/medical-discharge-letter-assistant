import streamlit as st
import tempfile
import os
from deep_translator import GoogleTranslator
from transformers import pipeline
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Load NLP Model for Summarization
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Predefined Medical Translations for Accuracy
medical_terms = {
    "Follow-up": "Nachkontrolle",
    "Low-sodium diet": "Natriumarme Diät",
    "Exercise": "Regelmäßige körperliche Aktivität",
    "Lifestyle modifications": "Empfohlene Lebensstiländerungen",
    "Blood pressure monitoring": "Blutdrucküberwachung",
    "Hypertension": "Hypertonie",
    "Diabetes management": "Diabetesmanagement",
    "Physical therapy": "Physiotherapie",
    "Cardiology consultation": "Kardiologische Nachsorge",
}

def translate_with_corrections(text):
    """Translate text and apply predefined medical translations."""
    translated_text = GoogleTranslator(source='auto', target='de').translate(text)
    for eng, ger in medical_terms.items():
        translated_text = translated_text.replace(eng, ger)
    return translated_text

# Streamlit UI - Improved Layout
st.set_page_config(page_title="Medical Discharge Letter Assistant", layout="wide")

st.title("🏥 Medical Discharge Letter Assistant 🇩🇪")
st.subheader("Helping Non-German Doctors Write Accurate Discharge Letters in German")

# Sidebar - User Input
st.sidebar.header("🔹 Enter Patient Information")
diagnosis = st.sidebar.text_area("🩺 Diagnosis (English)", "")
treatment = st.sidebar.text_area("💊 Treatment & Medications (English)", "")
recommendations = st.sidebar.text_area("📌 Follow-up Recommendations (English)", "")

# Generate Discharge Letter Button
if st.sidebar.button("Generate Discharge Letter"):
    if diagnosis and treatment and recommendations:  # Ensure fields are filled
        # Combine user input
        medical_text = f"Diagnosis: {diagnosis}. Treatment: {treatment}. Follow-up: {recommendations}."

        # AI Summarization
        summary = summarizer(medical_text, max_length=100, min_length=30, do_sample=False)[0]['summary_text']

        # AI Translation with Manual Editing
        translated_summary = st.text_area("📝 Edit Diagnosis (German)", translate_with_corrections(summary))
        translated_treatment = st.text_area("📝 Edit Treatment & Medications (German)", translate_with_corrections(treatment))
        translated_recommendations = st.text_area("📝 Edit Follow-up Recommendations (German)", translate_with_corrections(recommendations))

        # Final Discharge Letter
        st.subheader("📄 Final Discharge Letter")
        discharge_letter = f"""
        **Entlassungsbrief**
        
        **Diagnose:** {translated_summary}
        
        **Therapie:** {translated_treatment}
        
        **Empfehlung:** {translated_recommendations}
        """

        st.markdown(discharge_letter)

        # PDF Export Function
        def generate_pdf(content):
            temp_dir = tempfile.mkdtemp()
            pdf_filename = os.path.join(temp_dir, "Medical_Discharge_Letter.pdf")

            c = canvas.Canvas(pdf_filename, pagesize=letter)
            c.setFont("Helvetica", 12)

            c.drawString(200, 750, "Medical Discharge Letter")
            c.line(200, 745, 420, 745)

            y_position = 700
            for line in content.split("\n"):
                c.drawString(50, y_position, line)
                y_position -= 20
                if y_position < 50:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y_position = 750

            c.save()
            return pdf_filename

        # Add "Download PDF" Button
        pdf_file = generate_pdf(discharge_letter)
        with open(pdf_file, "rb") as file:
            st.download_button(
                label="📄 Download PDF",
                data=file,
                file_name="Medical_Discharge_Letter.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("⚠️ Please fill in all fields before generating the discharge letter.")
