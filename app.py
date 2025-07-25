
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import quote

st.title("🛒 Comparador de Precios de Supermercados")

producto = st.text_input("Ingresá un producto para buscar:", "Coca Cola 1.5 Litros")

def normalizar_producto(prod):
    prod = prod.lower().replace("1.5", "1500")
    return quote(prod)

def scrape_tualmacen(prod):
    url = f"https://tualmacen.com.ar/busqueda/{prod}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.select("div.item")
    resultados = []
    for item in items:
        nombre = item.select_one(".product-title")
        precio = item.select_one(".price")
        if nombre and precio:
            resultados.append({
                "Sitio": "TuAlmacen",
                "Producto": nombre.text.strip(),
                "Precio": precio.text.strip(),
            })
    return resultados

def scrape_toledo(prod):
    url = f"https://www.toledodigital.com.ar/{prod}?_q={prod}&map=ft"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.select("div.vtex-product-summary-2-x-container")
    resultados = []
    for item in items:
        nombre = item.select_one("span.vtex-product-summary-2-x-productBrand")
        precio = item.select_one("span.vtex-product-price-1-x-sellingPrice")
        if nombre and precio:
            resultados.append({
                "Sitio": "Toledo",
                "Producto": nombre.text.strip(),
                "Precio": precio.text.strip(),
            })
    return resultados

def scrape_cooperativa(prod):
    url = f"https://www.lacoopeencasa.coop/listado/busqueda-avanzada/{prod}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.select("div.lista-producto")
    resultados = []
    for item in items:
        nombre = item.select_one("h2")
        precio = item.select_one("span.precio")
        if nombre and precio:
            resultados.append({
                "Sitio": "La Coope",
                "Producto": nombre.text.strip(),
                "Precio": precio.text.strip(),
            })
    return resultados

if st.button("Buscar") and producto:
    st.subheader(f"Resultados para: {producto}")
    producto_normalizado = normalizar_producto(producto)
    resultados = []
    try:
        resultados += scrape_tualmacen(producto_normalizado)
    except:
        st.error("Error al acceder a TuAlmacen")
    try:
        resultados += scrape_toledo(producto_normalizado)
    except:
        st.error("Error al acceder a Toledo")
    try:
        resultados += scrape_cooperativa(producto_normalizado)
    except:
        st.error("Error al acceder a La Coope")

    if resultados:
        df = pd.DataFrame(resultados)
        df["Fecha"] = pd.Timestamp.now().strftime("%Y-%m-%d")
        st.dataframe(df[["Sitio", "Producto", "Precio", "Fecha"]])
    else:
        st.warning("No se encontraron resultados para ese producto.")
