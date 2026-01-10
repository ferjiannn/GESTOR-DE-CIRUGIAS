import streamlit as st
import json
import unicodedata

st.markdown("# STAFF ACCESS")

if "clicked" not in st.session_state:
    st.session_state.clicked = False

if "acceso" not in st.session_state:
    st.session_state.acceso = False

with open ("APP\data.json", "r", encoding = "utf-8") as Data:
    appdata = json.load(Data) 

staff = appdata.get("staff", {})
staff_data = staff
staff_list = []
    
for key in staff_data:
    categoria = staff_data.get(key)
        
    if isinstance(categoria, list):
        staff_list.extend(categoria)


input_name = st.text_input("NOMBRE")
input_id = st.text_input("IDENTIFICACIÓN")
   

def handle_click():
    st.session_state.clicked = True

st.button("ACCEDER", on_click=handle_click)

if st.session_state.clicked:
    acceso_concedido = False
    if acceso_concedido:
        st.session_state.ir_a_surgery = True

    for person in staff_list:
        if (
            person.get("nombre", "").strip()
        == input_name.strip()
        and person.get("id").strip()
        == input_id.strip()
    ):
            acceso_concedido = True
            break

    if acceso_concedido:
        st.session_state.acceso = True
        
    else:
        st.error("ACCESO DENEGADO")
    st.session_state.clicked = False

    if st.session_state.get("ir_a_surgery", False):
    
        st.session_state.ir_a_surgery = False
        st.switch_page("surgery")

        