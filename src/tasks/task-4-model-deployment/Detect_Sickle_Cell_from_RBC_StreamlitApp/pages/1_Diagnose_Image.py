

import streamlit as st
from streamlit.elements import text
from streamlit.components.v1 import iframe
import os
import io
from datetime import date
import glob as glob
import pandas as pd
import numpy as np
from PIL import Image
from ultralyticsplus import YOLO
from ultralyticsplus import render_result
import base64
#import plotly
import plotly.express as px
from project_utils import download_pdf

MODEL_PATH = './Models/Model2.pt'

ALLOWED_EXTENSIONS = ["jpg","jpeg","png"]

WARNING_MESSAGE='Disclaimer: This app is not intended to be a substitute for professional medical advice, diagnosis, or treatment. The predictions and information provided by the app are for educational and informational purposes only. The predictions are based on a model and may not always be accurate. Users should consult with a qualified healthcare provider before making any decisions based on the app''s predictions or information.'

WIDTH_IMAGE=380
HEIGHT_IMAGE=380
WIDTH_CHART=400
HEIGHT_CHART=400
WIDTH_PDF=300
HEIGHT_PDF=300

#PAGE_TITLE="Diagnose Sickle Cell Diseases by Red Blood Cells(RBCs) Classification"

HEADER_STYLE=f"""<style>
 	    [data-testid="stToolbar"]{{
	    top: -50px;
	    visibility: hidden;
	    }}			
            footer {{
            visibility: hidden;
            position: relative;
            }}
            footer:before {{
            visibility: visible;
            position: relative;
	    content: "Project by Omdena Benin Chapter - {date.today().year}";
	    display:block;
	    color:tomato; 
	    padding:50;
            }}
    table, th, td {{
		text-align: center !important;
		padding: 1px !important;
		border: 2px solid black !important;
		border-collapse: collapse !important;
		font-size: large !important;
		}}
</style>
"""

@st.cache_resource
def get_model(path):
  prediction_model = dict();
  prediction_model['model_object'] = YOLO(path)  #Yolov8n
  prediction_model['model_labelclass'] = pd.DataFrame(['Crystal','Normal',  'Others', 'Sickle', 'Target'],columns=["Classes"])
  return prediction_model

def modelpredict(model, upload_image_obj,detection_tuning_level):
  img_arr = np.array(upload_image_obj) 
  #predicted_result = model.predict(img_arr,verbose=False)
  predicted_result = model.predict(img_arr, exist_ok=True, conf=detection_tuning_level)
  return predicted_result

def detect_cell_disease(model_result,model_labelclass):
  cls=model_result[0].boxes.cls
  cls=pd.DataFrame(cls.numpy(),columns=["Classes"]).astype(int)
  cls["Count"]=0
  cls=cls.groupby("Classes").count()
  cls=pd.concat([model_labelclass,cls],axis=1).set_index("Classes").fillna(0).astype(int)
  return cls

def display_detected_classes_boundingboxes(imageobj,model_object,model_result):
  return render_result(imageobj,model=model_object,result=model_result[0])
  
def display_bar_chart(table_df):
  return px.bar(table_df, x="Classes", y="Count", color="Classes", orientation="v", hover_name="Classes", width=WIDTH_CHART, height=HEIGHT_CHART,
            #title="Detected Diseases Cells in RBC",
            color_discrete_sequence=["blue", "orange", "red", "green","yellow", "purple","pink","violet","maroon","olive","teal","cyan","brown"])

def display_doughnut_chart(table_df):
  return px.pie(table_df, values='Percentage', names='Classes', width=WIDTH_CHART, height=WIDTH_CHART, 
  #title='Pie Chart of Percentage as per their classes', 
  hover_data=['Count'], hole=0.4, color_discrete_sequence=["blue", "orange", "red", "green","yellow", "purple","pink","violet","maroon","olive","teal","cyan","brown"])
    
def RBC_status(RBCpercent): # RBC is given as DataFrame
  RBCpercent=RBCpercent[['Crystal', 'Normal', 'Others', 'Sickle', 'Target']]
  Crystal,N,Other,S,Target=RBCpercent.values[0]
  if Target*Crystal>0 and Crystal+Target>0.3 :
    C=Target+Crystal
  else:
    C=0
    N=N+Target+Crystal
  NO =N+Other
  HbDB=pd.DataFrame({"HbA":NO,"HbS":S,"HbC":C},index=["SCD Status"])
  if N>0.9 or S+C< 0.03 : 
   stat="AA"
  elif NO>=0.3 and S>0.03 and S>=C :
   stat="AS"
  elif NO>=0.3 and C>0.03 : 
   stat="AC"
  elif C>0.85 : 
   stat="CC"
  elif S>0.85 : 
   stat="SS"
  elif C>=0.4 and S>=0.4 : 
   stat="SC"
  else :
   stat="Non determined"
  HbDB["Status"]=stat
  return HbDB

    
model_obj = get_model(os.path.abspath(MODEL_PATH))

st.set_option('deprecation.showfileUploaderEncoding', False)
st.markdown(HEADER_STYLE, unsafe_allow_html=True)
#st.title(PAGE_TITLE)
with st.container():
    conf_value = st.slider(label='Select detection tuning level value between 0.0 and 1.0 for better performance: ', min_value=0.0, max_value=1.0, value=0.4, step=0.1) 
    st.title(f"Upload a RBC Image of Format(jpeg,jpg,png): ")
    uploaded_image_file = st.file_uploader("", type=ALLOWED_EXTENSIONS)
    st.warning(WARNING_MESSAGE, icon="⚠️")
    with st.container():
      if uploaded_image_file is not None:
        uploaded_image_filename=uploaded_image_file.name
        imageobj=Image.open(uploaded_image_file)
        model_predict_result=modelpredict(model_obj['model_object'], imageobj, conf_value)
        detected_cell_disease_df=detect_cell_disease(model_predict_result,model_obj['model_labelclass'])
        detected_cell_disease_boundingboxes=display_detected_classes_boundingboxes(imageobj,model_obj['model_object'], model_predict_result)
        RBC_status_df=RBC_status((detected_cell_disease_df/detected_cell_disease_df.sum()).T)
        detected_cell_disease_df.reset_index(inplace=True)
        detected_cell_disease_df.insert(2, 'Percentage', round(((detected_cell_disease_df['Count']/detected_cell_disease_df['Count'].sum())*100),2))
        bar_chart_fig=display_bar_chart(detected_cell_disease_df)
        doughnut_chart_fig=display_doughnut_chart(detected_cell_disease_df)
        
        col1, col2 = st.columns([6,6], gap="small")
        with col1:
          st.markdown('### **Uploaded Image**',unsafe_allow_html=True)
          st.image(imageobj,width=WIDTH_IMAGE)  #300 #640
        with col2:
          st.markdown('### **Diagnose disease cells**',unsafe_allow_html=True)
          st.image(detected_cell_disease_boundingboxes, width=WIDTH_IMAGE)
        col3, col4 = st.columns([8,4],gap="small")
        with col3:
          st.subheader(f"Total detected classified cells are: {detected_cell_disease_df['Count'].sum()}")
        with col4:
          st.download_button("⬇️ Download Report in PDF",
                    data=download_pdf(imageobj, detected_cell_disease_boundingboxes,detected_cell_disease_df, RBC_status_df, bar_chart_fig, doughnut_chart_fig,WIDTH_PDF,HEIGHT_PDF),
                    file_name= uploaded_image_filename.rsplit( ".", 1 )[ 0 ] + ".pdf", mime="application/octet-stream")
        
        st.subheader("Analysis of detected diseases cells")
        col5, col6 = st.columns([6,6], gap="small")
        #st.subheader('#### Detected Classification Cells are:   ') #,unsafe_allow_html=True)
        #st.markdown("<br>", unsafe_allow_html=True)
        with col5:
          #st.markdown(TABLE_STYLE, unsafe_allow_html=True)
          st.dataframe(detected_cell_disease_df)
        with col6:
          st.dataframe(RBC_status_df)
        st.markdown("<br>", unsafe_allow_html=True)  
        col7, col8 = st.columns([6,6], gap="small")
        with col7:
          st.plotly_chart(bar_chart_fig)        
        with col8:
          st.plotly_chart(doughnut_chart_fig)
