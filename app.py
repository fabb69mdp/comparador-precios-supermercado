
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import pandas as pd
from datetime import datetime

SITIOS = [
    {
        "nombre": "TuAlmacén",
        "url_busqueda": lambda query: f"https://tualmacen.com.ar/?s={quote_plus(query)}",
        "selector_item": ".product-small",
        "selector_nombre": ".woocommerce-loop-product__title",
        "selector_precio": ".price",
        "base_url": "https://tualmacen.com.ar"
    },
    {
        "nombre": "Cooperativa Obrera",
        "url_busqueda": lambda query: f"https://www.cooperativaobrera.coop/buscar?txtBusqueda={quote_plus(query)}",
        "selector_item": ".col-xs-12.col-sm-6.col-md-3.col-lg-3",
        "selector_nombre": ".descripcion_articulo",
        "selector_precio": ".precio_oferta",
        "base_url": "https://www.cooperativaobrera.coop"
    },
    {
        "nombre": "Toledo",
        "url_busqueda": lambda query: f"https://www.toledodigital.com.ar/catalogsearch/result/?q={quote_plus(query)}",
        "selector_item": ".product-item-info",
        "selector_nombre": ".product-item-name",
        "selector_precio": ".price",
        "base_url": "https://www.toledodigital.com.ar"
    },
]

def buscar_producto(sitio, consulta):
    resultados = []
    try:
        url = sitio["url_busqueda"](consulta)
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select(sitio["selector_item"])

        for item in items[:5]:
            try:
                nombre = item.select_one(sitio["selector_nombre"]).get_text(strip=True)
                precio = item.select_one(sitio["selector_precio"]).get_text(strip=True)
                resultados.append({
                    "Sitio": sitio["nombre"],
                    "Producto": nombre,
                    "Precio": precio,
                    "Link": url,
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            except:
                continue

    except Exception as e:
        resultados.append({
            "Sitio": sitio["nombre"],
            "Producto": "Error",
            "Precio": str(e),
            "Link": "-",
            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    return resultados

# Interfaz
st.set_page_config(page_title="Comparador de Precios", layout="wide")
st.title("🛒 Comparador de Precios de Supermercados")

consulta = st.text_input("🔍 Ingresá un producto para buscar:", "Coca Cola 1.5 Litros")

if "historial" not in st.session_state:
    st.session_state["historial"] = []

if st.button("Buscar") and consulta:
    resultados_totales = []
    with st.spinner("Buscando en supermercados..."):
        for sitio in SITIOS:
            resultados = buscar_producto(sitio, consulta)
            resultados_totales.extend(resultados)

    st.session_state["historial"].extend(resultados_totales)
    df = pd.DataFrame(resultados_totales)

    st.subheader(f"Resultados para: {consulta}")
    st.dataframe(df[["Sitio", "Producto", "Precio", "Fecha"]])

    if st.download_button("📥 Descargar resultados como CSV", data=df.to_csv(index=False), file_name="precios.csv"):
        st.success("Descarga iniciada.")

st.markdown("---")
st.subheader("📊 Historial de búsquedas en esta sesión")

if st.session_state["historial"]:
    df_hist = pd.DataFrame(st.session_state["historial"])
    st.dataframe(df_hist[["Sitio", "Producto", "Precio", "Fecha"]])
    st.download_button("📥 Descargar historial como CSV", data=df_hist.to_csv(index=False), file_name="historial.csv")
else:
    st.info("Todavía no buscaste ningún producto.")
