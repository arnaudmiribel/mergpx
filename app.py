import streamlit as st
import gpxpy

import os
import base64


def get_binary_file_downloader_html(data, file_label="File"):
    bin_str = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="merged.gpx">⬆️ Download merged .gpx file</a>'
    return href


st.title("🍁 Merge `.gpx` files!")
gpx_files = st.file_uploader(
    "Upload .gpx files to be merged", type="gpx", accept_multiple_files=True
)

if gpx_files:
    merge = st.button(f"Merge all {len(gpx_files)} uploaded files!")

    if merge:

        merged = gpxpy.gpx.GPX()

        for gpx_file in gpx_files:
            gpx = gpxpy.parse(gpx_file.read())
            for track in gpx.tracks:
                track.name = gpx_file.name
                merged.tracks.append(track)
            for route in gpx.routes:
                route.name = gpx_file.name
                merged.routes.append(route)
            for wp in gpx.waypoints:
                merged.waypoints.append(wp)

        st.markdown(
            get_binary_file_downloader_html(
                data=merged.to_xml(), file_label="Merged GPX"
            ),
            unsafe_allow_html=True,
        )

        import plotly.express as px
        import plotly.graph_objects as go
        import numpy as np
        import pandas as pd
        from gpx_converter import Converter

        wonderland = Converter(input_file="merged.gpx").gpx_to_dataframe()
        mapbox_access_token = open(".mapbox_token").read()
        px.set_mapbox_access_token(mapbox_access_token)

        fig = px.scatter_mapbox(
            wonderland,
            lat="latitude",
            lon="longitude",
            # hover_name="time",
            hover_data={
                "latitude": ":.2f",
                "longitude": ":.2f",
                # "alt_ft": ":, ft"
            },
            zoom=11,
            height=500,
        )

        fig.update_layout(
            margin=dict(r=0, t=0, l=0, b=0),
            # mapbox_style="white-bg",
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=go.layout.mapbox.Center(lat=44.8638281, lon=-0.656353),
                zoom=5,
            ),
        )

        # fig.update_traces(
        #    hovertemplate="<b>%{hovertext}</b><br><br>(%{customdata[0]:.2f}, %{customdata[1]:.2f})<br>Elev. %{customdata[2]:} .ft<extra></extra>"
        # )

        # fig.show()
        st.plotly_chart(fig)
