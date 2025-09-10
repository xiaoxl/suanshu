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

# Configure page
st.set_page_config(page_title="Math Pattern Generator", layout="wide")

st.title("Math Pattern Generator")


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


# Default values
default_num_pattern = """A1=random.randint(1,29)
A2=random.randint(10,99)
B1=random.randint(1,19)
B2=random.randint(10,99)
B3=10-B1
C1=random.randint(1,9)
C2=random.randint(10,99)
bA2=C1*10-A2 if C1*10>A2 else C1*100-A2
bA3=C1*10+A2"""

default_qtemplates = """(A1-B1)-C1 @1 &(0,)
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
A1-B1-C1 @1 &(0,)"""

# Sidebar for inputs
with st.sidebar:
    st.header("Configuration")

    # Input for number patterns
    st.subheader("Number Pattern")
    num_pattern = st.text_area(
        "Number Pattern Code", value=default_num_pattern, height=200, help="Python code to generate random numbers"
    )

    st.subheader("Question Templates")
    qtemplates_v2 = st.text_area(
        "Question Templates", value=default_qtemplates, height=300, help="Templates for generating math questions"
    )

    st.subheader("Settings")
    num_pages = st.slider("Number of Pages", 1, 10, 2)
    Ncol = st.slider("Columns per Page", 2, 6, 4)
    Nrow = st.slider("Rows per Page", 4, 12, 8)
    fontsize = st.slider("Font Size", 6, 20, 10)

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

    if hasattr(st.session_state, "worksheets") and st.session_state.worksheets:
        # Display PNG previews
        st.subheader("Worksheet Previews")
        for i, worksheet_buffer in enumerate(st.session_state.worksheets):
            st.write(f"**Page {i + 1}:**")
            # Display the image
            image = Image.open(BytesIO(worksheet_buffer.getvalue()))
            st.image(image, width=300)

        # Download individual PNGs
        st.subheader("Download Individual Pages")
        for i, worksheet_buffer in enumerate(st.session_state.worksheets):
            st.download_button(
                label=f"Download Page {i + 1} (PNG)",
                data=worksheet_buffer.getvalue(),
                file_name=f"math_worksheet_page_{i + 1}.png",
                mime="image/png",
                key=f"png_{i}",
            )

        # Download as PDF
        st.subheader("Download All Pages as PDF")
        if st.button("Create PDF", type="secondary"):
            try:
                pdf_buffer = create_pdf_from_images(st.session_state.worksheets)
                st.session_state.pdf_buffer = pdf_buffer
                st.success("PDF created successfully!")
            except Exception as e:
                st.error(f"Error creating PDF: {str(e)}")

        if hasattr(st.session_state, "pdf_buffer"):
            st.download_button(
                label="Download PDF",
                data=st.session_state.pdf_buffer.getvalue(),
                file_name="math_worksheets.pdf",
                mime="application/pdf",
            )

# Instructions
with st.expander("How to Use"):
    st.write("""
    1. **Template Presets**: Choose from predefined templates or select 'Custom' to create your own
    2. **Number Pattern**: Define variables using Python code with random.randint() etc.
    3. **Question Templates**: Each line should follow the format: `expression @weight &(min,max)`
       - `expression`: Mathematical expression using your defined variables
       - `@weight`: Probability weight for this template type
       - `&(min,max)`: Answer constraints (optional)
    4. **Settings**: Adjust layout and appearance
    5. **Generate**: Click "Generate Worksheets" to create PNG images
    6. **Download**: Preview and download individual PNGs or combine into PDF
    
    **Template Descriptions:**
    - **Basic Addition/Subtraction**: Simple operations with small numbers
    - **Multiplication/Division**: Times tables and basic division
    - **Large Number Operations**: Working with 2-3 digit numbers
    - **Mixed Operations**: Combining addition, subtraction, and multiplication
    - **Distributive Property**: Practice with distributive law (a+b)×c = ac+bc
    - **Custom**: Create your own templates
    
    **Example Template**: `A1+B1-C1 @1 &(0,)` creates problems like "5+3-2=" with positive answers
    """)

# Template Preview
with st.expander("📋 Current Template Preview"):
    st.write(f"**Selected Template:** {selected_template}")

    col_preview1, col_preview2 = st.columns(2)

    with col_preview1:
        st.write("**Variables:**")
        try:
            # Show what variables will be generated
            sample_vars = random_pattern(num_pattern)
            for var, val in sample_vars.items():
                st.write(f"- {var} = {val}")
        except Exception as e:
            st.error(f"Error in number pattern: {e}")

    with col_preview2:
        st.write("**Sample Problems:**")
        try:
            sample_problems = genqvault(qtemplates_v2, num_pattern, 3)
            for i, prob in enumerate(sample_problems):
                result = eval(prob)
                st.write(f"{i + 1}. {prob} = {result}")
        except Exception as e:
            st.error(f"Error generating samples: {e}")
