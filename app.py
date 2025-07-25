
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Comparador de Precios", layout="centered")

st.title("🛒 Comparador de Precios de Supermercados")
st.write("🔍 Ingresá un producto para buscar:")

query = st.text_input("")
buscar = st.button("Buscar")

resultados = []

def scrape_toledo(query):
    url = f"https://www.toledodigital.com.ar/catalogsearch/result/?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    productos = soup.select(".product-item")
    for p in productos:
        nombre = p.select_one(".product.name.product-item-name a")
        precio = p.select_one(".price")
        if nombre and precio:
            resultados.append({
                "Sitio": "Toledo",
                "Producto": nombre.text.strip(),
                "Precio": precio.text.strip(),
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

def scrape_cooperativa(query):
    url = f"https://www.cooperativaobrera.coop/sitios/cdo/catalogsearch/result/?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    productos = soup.select(".product-item")
    for p in productos:
        nombre = p.select_one(".product-item-link")
        precio = p.select_one(".price")
        if nombre and precio:
            resultados.append({
                "Sitio": "Cooperativa Obrera",
                "Producto": nombre.text.strip(),
                "Precio": precio.text.strip(),
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

def scrape_tualmacen(query):
    url = f"https://tualmacen.com.ar/search/?q={query.replace(' ', '%20')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    productos = soup.select(".product-card")
    for p in productos:
        nombre = p.select_one(".product-title")
        precio = p.select_one(".price-item")
        if nombre and precio:
            resultados.append({
                "Sitio": "TuAlmacén",
                "Producto": nombre.text.strip(),
                "Precio": precio.text.strip(),
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

if buscar and query.strip():
    st.subheader(f"Resultados para: {query}")
    with st.spinner("Buscando precios en supermercados..."):
        try:
            scrape_toledo(query)
            scrape_cooperativa(query)
            scrape_tualmacen(query)
            df = pd.DataFrame(resultados)
            if df.empty:
                st.warning("⚠️ No se encontraron resultados para esa búsqueda.")
            else:
                st.dataframe(df[["Sitio", "Producto", "Precio", "Fecha"]])
        except Exception as e:
            st.error(f"❌ Ocurrió un error: {e}")
