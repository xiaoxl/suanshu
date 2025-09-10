import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random
import re
from io import BytesIO
from PIL import Image
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
import os
import glob
from pathlib import Path

# Configure page
st.set_page_config(page_title="Math Pattern Generator", layout="wide")


# Your original functions
def renderlatex(expr):
    expr = expr.replace("*", "\\times ")
    expr = expr.replace("/", "\\div ")
    expr = "$" + expr + "$"
    return expr


def randomsample(plist, numofselections):
    NN = len(plist)
    qq = numofselections // NN
    rr = numofselections - NN * qq
    rlist = random.sample(plist, rr)
    return plist * qq + rlist


def lastnonzero(ls):
    tmpls = [i for i, e in enumerate(ls) if e != 0]
    if tmpls != []:
        ind = tmpls[-1]
    else:
        ind = -1
    return ind


def random_pattern(num_pattern):
    nums = [num for num in num_pattern.split("\n") if len(num) != 0]
    numdict = {}
    local_vars = {"random": random}
    for _num in nums:
        v = _num.split("=")[0]
        exec(_num, {}, local_vars)
        numdict[v] = str(local_vars[v])
    return numdict


def generateq(ptem, num_pattern):
    numdict = random_pattern(num_pattern)
    pattern = re.compile("|".join(re.escape(k) for k in numdict))
    result = pattern.sub(lambda m: numdict[m.group(0)], ptem)
    return result


def genqvault(qtemplates, num_pattern, N=10):
    qtlist = qtemplates.split("\n")
    qtlist = [x for x in qtlist if x != ""]
    qlist = list()
    qdlist = list()
    qclist = list()
    plist = list()
    M = len(qtlist)

    for qtype in qtlist:
        qp, qd = qtype.split("@")
        qd, qc = qd.split("&")
        qcl = re.findall(r"(\d+)\s*,", qc)
        qcr = re.findall(r",\s*(\d+)", qc)
        amin = None
        amax = None
        if len(qcl) != 0:
            amin = int(qcl[0])
        if len(qcr) != 0:
            amax = int(qcr[0])
        qdlist.append(qd)
        qlist.append(qp)
        qclist.append((amin, amax))

    qdlist = np.array(qdlist, dtype=int)
    pp = qdlist / qdlist.sum()
    rqdlist = np.random.choice(list(range(M)), size=N, p=pp)

    for i in rqdlist:
        amin = qclist[i][0]
        amax = qclist[i][1]
        flag = 1
        while flag:
            prob = generateq(qlist[i], num_pattern)
            try:
                ans = eval(prob)
                if ans != int(ans):
                    continue
                if amin is not None:
                    if ans < amin:
                        continue
                if amax is not None:
                    if ans > amax:
                        continue
                flag = 0
            except:
                continue
        plist.append(prob)

    return plist


def create_math_worksheet(plist, Ncol=4, Nrow=8, fontsize=10):
    """Create a math worksheet using your original layout"""
    colModifier = 0.03
    rowModifier = 0.1

    collist = [c / Ncol + colModifier for c in range(Ncol)]
    rowlist = [r / Nrow + rowModifier for r in range(Nrow)]

    fig, ax = plt.subplots(figsize=(8.5, 11), dpi=300)

    for i in range(Nrow):
        for j in range(Ncol):
            if i * Ncol + j < len(plist):
                ax.text(collist[j], rowlist[i], renderlatex(plist[i * Ncol + j]) + "=", fontsize=fontsize)

    plt.axis("off")

    # Convert to PNG bytes
    img_buffer = BytesIO()
    plt.savefig(img_buffer, pad_inches=0, format="png", bbox_inches="tight")
    plt.close()
    img_buffer.seek(0)

    return img_buffer


def create_pdf_from_images(image_buffers):
    """Create a PDF from multiple PNG images"""
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    for img_buffer in image_buffers:
        # Create temporary file for image
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            tmp_file.write(img_buffer.getvalue())
            tmp_file_path = tmp_file.name

        try:
            # Add image to PDF
            c.drawImage(tmp_file_path, 0, 0, width=612, height=792)  # Letter size
            c.showPage()
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer


# Template management functions
def load_template_from_file(filepath):
    """Load template from file with --- separator"""
    try:
        with open(filepath, "r") as f:
            content = f.read().strip()

        if "---" in content:
            parts = content.split("---", 1)
            num_pattern = parts[0].strip()
            qtemplates = parts[1].strip()
            return {"num_pattern": num_pattern, "qtemplates": qtemplates}
        else:
            return None
    except Exception:
        return None


def save_template_to_file(name, num_pattern, qtemplates):
    """Save template to file with --- separator"""
    try:
        # Create templates directory if it doesn't exist
        os.makedirs("templates", exist_ok=True)

        filepath = f"templates/{name}.txt"
        content = f"{num_pattern}\n---\n{qtemplates}"

        with open(filepath, "w") as f:
            f.write(content)
        return True
    except Exception as e:
        st.error(f"Error saving template: {e}")
        return False


def get_available_templates():
    """Get list of available template files"""
    try:
        os.makedirs("templates", exist_ok=True)
        template_files = glob.glob("templates/*.txt")
        template_names = [Path(f).stem for f in template_files]
        return sorted(template_names)
    except Exception:
        return []


def get_next_template_number():
    """Get the next available template number"""
    existing_templates = get_available_templates()
    numbers = []
    for template in existing_templates:
        if template.startswith("template") and template[8:].isdigit():
            numbers.append(int(template[8:]))

    if numbers:
        return max(numbers) + 1
    else:
        return 1


# ============================================================================
# MAIN APP STARTS HERE
# ============================================================================

st.title("Math Pattern Generator")

# Initialize session state
if "selected_template_name" not in st.session_state:
    st.session_state.selected_template_name = None
if "template_data" not in st.session_state:
    st.session_state.template_data = None
if "template_saved" not in st.session_state:
    st.session_state.template_saved = False

# Template switcher at the top
st.markdown("### 📋 Template Manager")
col1, col2 = st.columns([3, 1])

with col1:
    # Get available templates
    available_templates = get_available_templates()
    template_options = available_templates + ["+ Create New Template"]

    # Set default selection
    default_index = 0 if available_templates else len(template_options) - 1

    selected_template = st.selectbox("Choose Template:", template_options, index=default_index, key="template_selector")

with col2:
    if st.button("🔄 Refresh Templates"):
        st.session_state.selected_template_name = None
        st.rerun()

# with col3:
#     # Set default value based on whether template was just saved
#     default_name = "" if st.session_state.template_saved else f"template{get_next_template_number()}"
#     new_template_name = st.text_input("New Template Name:", placeholder=default_name, key="new_template_name")

# with col4:
#     save_template = st.button("💾 Save", help="Save current configuration as new template")

# Reset template_saved flag after displaying the input
if st.session_state.template_saved:
    st.session_state.template_saved = False

# Load template data when selection changes
if st.session_state.selected_template_name != selected_template:
    st.session_state.selected_template_name = selected_template

    if selected_template == "+ Create New Template":
        # Default template for new creation
        st.session_state.template_data = {
            "num_pattern": """A1=random.randint(1,29)
A2=random.randint(10,99)
B1=random.randint(1,19)
B2=random.randint(10,99)
B3=10-B1
C1=random.randint(1,9)
C2=random.randint(10,99)
bA2=C1*10-A2 if C1*10>A2 else C1*100-A2
bA3=C1*10+A2""",
            "qtemplates": """(A1-B1)-C1 @1 &(0,)
(A1-B1)+C1 @1 &(0,)
(A1+B1)-C1 @1 &(0,)
(A1+B1)+C1 @1 &(0,)
C1-(A1-B1) @1 &(0,)
C1+(A1-B1) @1 &(0,)
C1-(A1+B1) @1 &(0,)
C1+(A1+B1) @1 &(0,)
A1+B1+C1 @1 &(0,)
A1+B1-C1 @1 &(0,)
A1-B1+C1 @1 &(0,)
A1-B1-C1 @1 &(0,)""",
        }
    else:
        # Load selected template
        template_path = f"templates/{selected_template}.txt"
        loaded_data = load_template_from_file(template_path)
        if loaded_data is None:
            st.error(f"Could not load template: {selected_template}")
            st.session_state.template_data = {"num_pattern": "A1=random.randint(1,10)", "qtemplates": "A1 @1 &(0,)"}
        else:
            st.session_state.template_data = loaded_data

# Get current template data
current_template_data = (
    st.session_state.template_data
    if st.session_state.template_data
    else {"num_pattern": "A1=random.randint(1,10)", "qtemplates": "A1 @1 &(0,)"}
)



# Handle template saving
# if save_template:
#     if new_template_name:
#         # Get current values from session state
#         if hasattr(st.session_state, "current_num_pattern") and hasattr(st.session_state, "current_qtemplates"):
#             success = save_template_to_file(
#                 new_template_name, st.session_state.current_num_pattern, st.session_state.current_qtemplates
#             )
#             if success:
#                 st.success(f"✅ Template '{new_template_name}' saved!")
#                 # Set flag to clear the name field on next render
#                 st.session_state.template_saved = True
#                 st.rerun()
#         else:
#             # Fallback - save current displayed values
#             success = save_template_to_file(
#                 new_template_name, current_template_data["num_pattern"], current_template_data["qtemplates"]
#             )
#             if success:
#                 st.success(f"✅ Template '{new_template_name}' saved!")
#                 st.session_state.template_saved = True
#                 st.rerun()
#     else:
#         st.warning("Please enter a template name.")

# Sidebar for inputs
with st.sidebar:
    st.header("Configuration")

    # Input for number patterns - use current template data as value
    # st.subheader("Number Pattern")
    num_pattern = st.text_area(
        "Number Pattern Code",
        value=current_template_data["num_pattern"],
        height=150,
        help="Python code to generate random numbers",
        key="current_num_pattern",
    )

    # st.subheader("Question Templates")
    qtemplates_v2 = st.text_area(
        "Question Templates",
        value=current_template_data["qtemplates"],
        height=250,
        help="Templates for generating math questions",
        key="current_qtemplates",
    )

    # Save Template option (moved here)
    # st.subheader("💾 Save Template")
    default_name = "" if st.session_state.template_saved else f"template{get_next_template_number()}"
    new_template_name = st.text_input("New Template Name:", placeholder=default_name, key="new_template_name_sidebar")

    if st.button("💾 Save Current Template", key="save_template_sidebar"):
        if new_template_name:
            success = save_template_to_file(
                new_template_name,
                st.session_state.current_num_pattern,
                st.session_state.current_qtemplates,
            )
            if success:
                st.success(f"✅ Template '{new_template_name}' saved!")
                st.session_state.template_saved = True
                st.rerun()
        else:
            st.warning("Please enter a template name.")

    st.subheader("Settings")
    num_pages = st.slider("Number of Pages", 1, 10, 2)
    Ncol = st.slider("Columns per Page", 2, 6, 4)
    Nrow = st.slider("Rows per Page", 4, 12, 8)
    fontsize = st.slider("Font Size", 6, 20, 10)

    # Template Preview in sidebar
    st.subheader("📋 Template Preview")
    if st.session_state.selected_template_name == "+ Create New Template":
        st.write("**Current:** New Template")
    elif st.session_state.selected_template_name:
        st.write(f"**Current:** {st.session_state.selected_template_name}")
    else:
        st.write("**Current:** None")

    with st.expander("Show Variables & Samples"):
        col_preview1, col_preview2 = st.columns([1, 1])

        with col_preview1:
            st.write("**Variables:**")
            try:
                # Show what variables will be generated using current values
                sample_vars = random_pattern(num_pattern)
                for var, val in sample_vars.items():
                    st.write(f"{var}={val}")
            except Exception as e:
                st.error(f"Error: {e}")

        with col_preview2:
            st.write("**Samples:**")
            try:
                sample_problems = genqvault(qtemplates_v2, num_pattern, 2)
                for i, prob in enumerate(sample_problems):
                    result = eval(prob)
                    st.write(f"{prob}={result}")
            except Exception as e:
                st.error(f"Error: {e}")

    # Delete template option
    if (
        st.session_state.selected_template_name
        and st.session_state.selected_template_name != "+ Create New Template"
        and available_templates
    ):
        st.subheader("⚠️ Delete Template")
        if st.button("🗑️ Delete Current Template", help="Permanently delete this template file"):
            try:
                template_path = f"templates/{st.session_state.selected_template_name}.txt"
                os.remove(template_path)
                st.success(f"Deleted template: {st.session_state.selected_template_name}")
                # Reset to create new template after deletion
                st.session_state.selected_template_name = None
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting template: {e}")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Math Worksheet Generator")

    if st.button("Generate Worksheets", type="primary"):
        try:
            # Generate worksheets
            worksheets = []
            problems_per_page = Ncol * Nrow

            progress_bar = st.progress(0)

            for page in range(num_pages):
                # Generate problems for this page
                plist = genqvault(qtemplates_v2, num_pattern, problems_per_page)

                # Create worksheet image
                img_buffer = create_math_worksheet(plist, Ncol, Nrow, fontsize)
                worksheets.append(img_buffer)

                # Update progress
                progress_bar.progress((page + 1) / num_pages)

            st.session_state.worksheets = worksheets
            st.success(f"Generated {len(worksheets)} worksheet pages!")

        except Exception as e:
            st.error(f"Error generating worksheets: {str(e)}")
            st.error("Please check your number pattern and question templates for syntax errors.")

    # Display sample problems if worksheets exist
    if hasattr(st.session_state, "worksheets"):
        st.subheader("Sample Problems")
        try:
            # Generate a small sample to show
            sample_problems = genqvault(qtemplates_v2, num_pattern, 6)
            for i, prob in enumerate(sample_problems):
                result = eval(prob)
                st.write(f"{i + 1}. {prob} = {result}")
        except Exception as e:
            st.warning(f"Could not generate sample: {str(e)}")

with col2:
    st.header("Preview & Download")

    # Generate and Download PDF buttons BEFORE worksheet previews
    if hasattr(st.session_state, "worksheets") and st.session_state.worksheets:
        # Download as PDF section
        st.subheader("📄 Download All Pages as PDF")

        # Pre-create PDF when worksheets exist for immediate download
        try:
            pdf_buffer = create_pdf_from_images(st.session_state.worksheets)
            st.download_button(
                label="📄 Create and Download PDF",
                data=pdf_buffer.getvalue(),
                file_name="math_worksheets.pdf",
                mime="application/pdf",
                type="secondary",
            )
        except Exception as e:
            st.error(f"Error creating PDF: {str(e)}")

        # Display PNG previews AFTER the PDF buttons
        st.subheader("🖼️ Worksheet Previews")
        for i, worksheet_buffer in enumerate(st.session_state.worksheets):
            st.write(f"**Page {i + 1}:**")
            # Display the image
            image = Image.open(BytesIO(worksheet_buffer.getvalue()))
            st.image(image, width=300)

        # Download individual PNGs
        st.subheader("📥 Download Individual Pages")
        for i, worksheet_buffer in enumerate(st.session_state.worksheets):
            st.download_button(
                label=f"Download Page {i + 1} (PNG)",
                data=worksheet_buffer.getvalue(),
                file_name=f"math_worksheet_page_{i + 1}.png",
                mime="image/png",
                key=f"png_{i}",
            )

# Instructions
with st.expander("How to Use"):
    st.write("""
    ## 📋 Template Management
    - **Choose Template**: Select from saved templates or "Create New Template"
    - **Save Template**: Enter name and click "💾 Save" to create template files
    - **Template Files**: Saved as `template1.txt`, `template2.txt`, etc. in `templates/` folder
    - **File Format**: 
      ```
      A1=random.randint(1,10)
      A2=random.randint(10,99)
      ---
      A1+A2 @1 &(0,)
      A1-A2 @1 &(0,)
      ```
    
    ## 🔧 Configuration
    1. **Number Pattern**: Define variables using Python code with random.randint() etc.
    2. **Question Templates**: Each line should follow the format: `expression @weight &(min,max)`
       - `expression`: Mathematical expression using your defined variables
       - `@weight`: Probability weight for this template type
       - `&(min,max)`: Answer constraints (optional)
    3. **Settings**: Adjust layout and appearance
    4. **Generate**: Click "Generate Worksheets" to create PNG images
    5. **Download**: Preview and download individual PNGs or combine into PDF
    
    **Example Template**: `A1+B1-C1 @1 &(0,)` creates problems like "5+3-2=" with positive answers
    """)
