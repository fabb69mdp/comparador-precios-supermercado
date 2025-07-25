import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.title("Buscador de productos")

def normalizar(texto):
    texto = texto.lower()
    texto = re.sub(r"[^a-zA-Z0-9áéíóúüñ\s]", "", texto)
    return texto

def hay_match(nombre_producto, consulta):
    nombre_normal = normalizar(nombre_producto)
    consulta_normal = normalizar(consulta)
    return all(p in nombre_normal for p in consulta_normal.split())

def buscar_toledo(consulta):
    resultados = []
    query = consulta.replace(" ", "%20")
    url = f"https://www.toledodigital.com.ar/{query}?_q={query}&map=ft"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select("div.vtex-product-summary-2-x-container")
        for item in items:
            nombre_el = item.select_one("span.vtex-product-summary-2-x-productBrand")
            desc_el = item.select_one("span.vtex-product-summary-2-x-productName")
            precio_el = item.select_one("span.vtex-product-price-1-x-currencyContainer")
            if not (nombre_el and desc_el and precio_el):
                continue
            nombre = nombre_el.text.strip() + " " + desc_el.text.strip()
            precio = precio_el.text.strip().replace("$", "").replace(".", "").replace(",", ".")
            try:
                precio = float(precio)
            except:
                continue
            if hay_match(nombre, consulta):
                resultados.append({"origen": "Toledo", "nombre": nombre, "precio": precio, "url": url})
    except:
        pass
    return resultados

def buscar_tualmacen(consulta):
    resultados = []
    query = consulta.replace(" ", "%20")
    url = f"https://tualmacen.com.ar/busqueda/{query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        productos = soup.select("div.product-box")
        for prod in productos:
            nombre_el = prod.select_one("a.name")
            precio_el = prod.select_one("div.price span")
            if not (nombre_el and precio_el):
                continue
            nombre = nombre_el.text.strip()
            precio = precio_el.text.strip().replace("$", "").replace(".", "").replace(",", ".")
            try:
                precio = float(precio)
            except:
                continue
            if hay_match(nombre, consulta):
                resultados.append({"origen": "TuAlmacen", "nombre": nombre, "precio": precio, "url": url})
    except:
        pass
    return resultados

def buscar_lacoope(consulta):
    resultados = []
    query = consulta.replace(" ", "_")
    url = f"https://www.lacoopeencasa.coop/listado/busqueda-avanzada/{query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select("div.product-card")
        for item in items:
            nombre_el = item.select_one("h2.product-card-title")
            precio_el = item.select_one("div.product-card-price-final")
            if not (nombre_el and precio_el):
                continue
            nombre = nombre_el.text.strip()
            precio = precio_el.text.strip().replace("$", "").replace(".", "").replace(",", ".")
            try:
                precio = float(precio)
            except:
                continue
            if hay_match(nombre, consulta):
                resultados.append({"origen": "LaCoope", "nombre": nombre, "precio": precio, "url": url})
    except:
        pass
    return resultados

consulta = st.text_input("¿Qué producto estás buscando?", value="coca cola 1.5")

if st.button("Buscar"):
    st.write("Buscando en sitios...")
    resultados = (
        buscar_toledo(consulta)
        + buscar_tualmacen(consulta)
        + buscar_lacoope(consulta)
    )
    if resultados:
        for res in sorted(resultados, key=lambda x: x["precio"]):
            st.markdown(f"**{res['origen']}** - {res['nombre']} - ${res['precio']:.2f}")
            st.markdown(f"[Ver producto]({res['url']})")
    else:
        st.warning("No se encontraron resultados relevantes.")