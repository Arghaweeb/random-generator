"""
Streamlit Web Interface for RNGaaS PoC
======================================
A user-friendly interface for interacting with the Random Number Generator as a Service.
"""

import streamlit as st
import requests
import json
import base64
from datetime import datetime
from typing import Dict, Any, List, Optional
import time

# Configuration
DEFAULT_SERVER_URL = "http://localhost:8000"
DEFAULT_API_KEY = "dev-key-12345"

# Page configuration
st.set_page_config(
    page_title="RNGaaS Control Panel",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'api_responses' not in st.session_state:
    st.session_state.api_responses = []
if 'server_url' not in st.session_state:
    st.session_state.server_url = DEFAULT_SERVER_URL
if 'api_key' not in st.session_state:
    st.session_state.api_key = DEFAULT_API_KEY


def add_api_response(endpoint: str, method: str, status: int, response_data: Any, error: Optional[str] = None):
    """Add an API response to the history."""
    st.session_state.api_responses.insert(0, {
        'timestamp': datetime.now().isoformat(),
        'endpoint': endpoint,
        'method': method,
        'status': status,
        'response': response_data,
        'error': error
    })
    # Keep only last 20 responses
    if len(st.session_state.api_responses) > 20:
        st.session_state.api_responses = st.session_state.api_responses[:20]


def make_request(method: str, endpoint: str, **kwargs) -> tuple[int, Any, Optional[str]]:
    """Make an API request and handle errors."""
    url = f"{st.session_state.server_url}{endpoint}"
    headers = kwargs.get('headers', {})
    headers['X-API-Key'] = st.session_state.api_key
    kwargs['headers'] = headers

    try:
        if method == 'GET':
            response = requests.get(url, **kwargs)
        elif method == 'POST':
            response = requests.post(url, **kwargs)
        else:
            return 400, None, f"Unsupported method: {method}"

        try:
            data = response.json()
        except:
            data = response.text

        return response.status_code, data, None
    except requests.exceptions.ConnectionError:
        return 0, None, f"Connection error: Cannot reach {url}"
    except Exception as e:
        return 0, None, f"Error: {str(e)}"


# Sidebar
with st.sidebar:
    st.title("🎲 RNGaaS Control Panel")
    st.markdown("---")

    # Server configuration
    st.subheader("Server Configuration")
    server_url = st.text_input("Server URL", value=st.session_state.server_url)
    api_key = st.text_input("API Key", value=st.session_state.api_key, type="password")

    if st.button("Update Configuration"):
        st.session_state.server_url = server_url
        st.session_state.api_key = api_key
        st.success("Configuration updated!")

    st.markdown("---")

    # Navigation
    st.subheader("Navigation")
    page = st.radio(
        "Select View:",
        ["System Status", "Request Random Data", "Node Configuration", "Manual Chunk Upload", "API Response Log"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption(f"Connected to: {st.session_state.server_url}")


# Main content area
st.title("RNGaaS Control Panel")
st.markdown("Random Number Generator as a Service - Web Interface")

# ============================================================================
# SYSTEM STATUS PAGE
# ============================================================================
if page == "System Status":
    st.header("📊 System Status")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("Monitor the overall system health and connected nodes")
    with col2:
        auto_refresh = st.checkbox("Auto-refresh (5s)", value=False)

    if st.button("🔄 Refresh Status") or auto_refresh:
        status_code, data, error = make_request('GET', '/v1/status')
        add_api_response('/v1/status', 'GET', status_code, data, error)

        if error:
            st.error(f"❌ {error}")
        elif status_code == 200:
            st.success(f"✅ Status retrieved successfully (Status: {status_code})")

            # Global statistics
            st.subheader("Global Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Global Buffer", f"{data['global_buffer_bytes']:,} bytes")
            with col2:
                st.metric("Total Nodes", data['total_nodes'])
            with col3:
                buffer_mb = data['global_buffer_bytes'] / (1024 * 1024)
                st.metric("Buffer Size", f"{buffer_mb:.2f} MB")

            # Node details
            st.subheader("Connected Nodes")
            if data['nodes']:
                for node in data['nodes']:
                    with st.expander(f"🖥️ {node['node_id']}", expanded=True):
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            status_emoji = "🟢" if node['status'] == 'ok' else "🟡" if node['status'] == 'degraded' else "🔴"
                            st.write(f"**Status:** {status_emoji} {node['status']}")
                            st.write(f"**State:** {node.get('state', 'N/A')}")
                            st.write(f"**Mode:** {node.get('mode', 'N/A')}")

                        with col2:
                            st.write(f"**Buffer:** {node['buffer_bytes']:,} bytes")
                            st.write(f"**Capacity:** {node['buffer_capacity']:,} bytes")
                            buffer_pct = (node['buffer_bytes'] / node['buffer_capacity'] * 100) if node['buffer_capacity'] > 0 else 0
                            st.progress(buffer_pct / 100, text=f"{buffer_pct:.1f}% full")

                        with col3:
                            st.write(f"**Last Seen:** {node.get('last_heartbeat', 'N/A')}")
                            if node.get('last_error'):
                                st.error(f"**Error:** {node['last_error']}")
                            else:
                                st.write("**Error:** None")
            else:
                st.info("No nodes currently connected")
        else:
            st.error(f"❌ Request failed with status {status_code}")
            st.json(data)

    # Auto-refresh logic
    if auto_refresh:
        time.sleep(5)
        st.rerun()


# ============================================================================
# REQUEST RANDOM DATA PAGE
# ============================================================================
elif page == "Request Random Data":
    st.header("🎲 Request Random Data")
    st.markdown("Request random bytes from the RNGaaS global buffer")

    col1, col2 = st.columns(2)
    with col1:
        num_bytes = st.number_input("Number of Bytes", min_value=1, max_value=1048576, value=32, step=1)
    with col2:
        format_type = st.selectbox("Output Format", ["hex", "b64"])

    if st.button("🎲 Generate Random Data", type="primary"):
        params = {"bytes": num_bytes, "format": format_type}
        status_code, data, error = make_request('GET', '/v1/random', params=params)
        add_api_response(f'/v1/random?bytes={num_bytes}&format={format_type}', 'GET', status_code, data, error)

        if error:
            st.error(f"❌ {error}")
        elif status_code == 200:
            st.success(f"✅ Random data generated successfully (Status: {status_code})")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Bytes Returned", data['bytes'])
            with col2:
                st.metric("Format", data['format'])
            with col3:
                st.metric("Timestamp", data['timestamp'].split('T')[1][:8])

            st.subheader("Random Data")
            st.code(data['value'], language="text")

            # Download button
            st.download_button(
                label="📥 Download Random Data",
                data=data['value'],
                file_name=f"random_{num_bytes}_{format_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

            # Show raw response
            with st.expander("View Raw JSON Response"):
                st.json(data)
        else:
            st.error(f"❌ Request failed with status {status_code}")
            st.json(data)


# ============================================================================
# NODE CONFIGURATION PAGE
# ============================================================================
elif page == "Node Configuration":
    st.header("⚙️ Node Configuration")
    st.markdown("Inspect configuration for a specific node")

    node_id = st.text_input("Node ID", value="node-001", placeholder="e.g., node-001")

    if st.button("🔍 Get Node Configuration", type="primary"):
        endpoint = f"/v1/nodes/{node_id}/config"
        status_code, data, error = make_request('GET', endpoint)
        add_api_response(endpoint, 'GET', status_code, data, error)

        if error:
            st.error(f"❌ {error}")
        elif status_code == 200:
            st.success(f"✅ Configuration retrieved for node '{node_id}' (Status: {status_code})")

            # Display configuration in organized sections
            st.subheader("Node Configuration")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Control Settings**")
                control = data.get('control', {})
                st.info(f"**Target State:** {control.get('target_state', 'N/A')}")
                st.info(f"**Surplus Allowed:** {control.get('surplus_allowed', 'N/A')}")
                max_buffer = control.get('max_buffer_bytes', 'N/A')
                max_buffer_str = f"{max_buffer:,}" if isinstance(max_buffer, int) else max_buffer
                st.info(f"**Max Buffer:** {max_buffer_str} bytes")

            with col2:
                st.markdown("**Node Identity**")
                st.info(f"**Node ID:** {node_id}")
                st.info(f"**Timestamp:** {data.get('timestamp', 'N/A')}")

            # Show full JSON
            with st.expander("View Complete Configuration JSON"):
                st.json(data)
        elif status_code == 404:
            st.warning(f"⚠️ Node '{node_id}' not found")
        else:
            st.error(f"❌ Request failed with status {status_code}")
            st.json(data)


# ============================================================================
# MANUAL CHUNK UPLOAD PAGE
# ============================================================================
elif page == "Manual Chunk Upload":
    st.header("📤 Manual Chunk Upload")
    st.markdown("Manually simulate a node uploading a random data chunk")

    st.info("💡 This simulates what a node daemon does when uploading entropy to the server")

    col1, col2 = st.columns(2)
    with col1:
        node_id = st.text_input("Node ID", value="manual-node-001", placeholder="e.g., node-001")
        chunk_id = st.text_input("Chunk ID", value=f"chunk-{int(time.time())}", placeholder="e.g., chunk-123")
        sequence = st.number_input("Sequence Number", min_value=0, value=1, step=1)

    with col2:
        entropy_source = st.text_input("Entropy Source", value="os.urandom", placeholder="e.g., os.urandom")
        conditioner = st.text_input("Conditioner", value="sha256", placeholder="e.g., sha256")
        data_length = st.number_input("Data Length (bytes)", min_value=1, max_value=1048576, value=1024, step=1)

    # Health metrics
    st.subheader("Health Metrics")
    col1, col2 = st.columns(2)
    with col1:
        bit_balance = st.slider("Bit Balance", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    with col2:
        health_status = "healthy" if 0.45 <= bit_balance <= 0.55 else "degraded"
        st.metric("Health Status", health_status)

    # Data input options
    st.subheader("Random Data")
    data_option = st.radio("Data Source:", ["Generate Random Data", "Enter Custom Data (Base64)"])

    if data_option == "Generate Random Data":
        st.info(f"Will generate {data_length} random bytes using os.urandom()")
        data_b64 = None
    else:
        custom_data = st.text_area("Base64 Encoded Data", placeholder="Enter base64 encoded data here...")
        if custom_data:
            try:
                # Validate base64
                base64.b64decode(custom_data)
                data_b64 = custom_data
                data_length = len(base64.b64decode(custom_data))
                st.success(f"✅ Valid base64 data ({data_length} bytes)")
            except:
                st.error("❌ Invalid base64 data")
                data_b64 = None
        else:
            data_b64 = None

    if st.button("📤 Upload Chunk", type="primary"):
        # Generate or use custom data
        if data_option == "Generate Random Data":
            import os
            random_bytes = os.urandom(data_length)
            data_b64 = base64.b64encode(random_bytes).decode('ascii')

        if not data_b64:
            st.error("❌ No data to upload. Please generate or enter valid base64 data.")
        else:
            # Construct chunk payload
            chunk_payload = {
                "node_id": node_id,
                "chunk_id": chunk_id,
                "sequence": sequence,
                "created_at": datetime.now().isoformat(),
                "length_bytes": data_length,
                "entropy_source": entropy_source,
                "conditioner": conditioner,
                "data_b64": data_b64,
                "health": {
                    "bit_balance": bit_balance,
                    "status": health_status
                }
            }

            endpoint = f"/v1/nodes/{node_id}/chunks"
            status_code, data, error = make_request('POST', endpoint, json=chunk_payload)
            add_api_response(endpoint, 'POST', status_code, data, error)

            if error:
                st.error(f"❌ {error}")
            elif status_code == 200:
                st.success(f"✅ Chunk uploaded successfully (Status: {status_code})")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Chunk ID", chunk_id)
                with col2:
                    st.metric("Size", f"{data_length:,} bytes")
                with col3:
                    st.metric("Health", health_status)

                # Show response
                with st.expander("View Server Response"):
                    st.json(data)

                # Show what was uploaded
                with st.expander("View Uploaded Chunk Data"):
                    st.json(chunk_payload)
            else:
                st.error(f"❌ Upload failed with status {status_code}")
                st.json(data)


# ============================================================================
# API RESPONSE LOG PAGE
# ============================================================================
elif page == "API Response Log":
    st.header("📋 API Response Log")
    st.markdown("Recent API interactions and responses")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"Showing last {len(st.session_state.api_responses)} API responses")
    with col2:
        if st.button("🗑️ Clear Log"):
            st.session_state.api_responses = []
            st.rerun()

    if not st.session_state.api_responses:
        st.info("No API responses yet. Make some requests to see them here!")
    else:
        for i, response in enumerate(st.session_state.api_responses):
            status_emoji = "✅" if 200 <= response['status'] < 300 else "❌" if response['status'] >= 400 else "⚠️"

            with st.expander(
                f"{status_emoji} [{response['method']}] {response['endpoint']} - {response['timestamp'].split('T')[1][:8]}",
                expanded=(i == 0)
            ):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Method:** {response['method']}")
                with col2:
                    st.write(f"**Status:** {response['status']}")
                with col3:
                    st.write(f"**Timestamp:** {response['timestamp']}")

                if response['error']:
                    st.error(f"**Error:** {response['error']}")
                else:
                    st.success("**Status:** Success")

                st.subheader("Response Data")
                if isinstance(response['response'], dict):
                    st.json(response['response'])
                else:
                    st.code(str(response['response']))


# Footer
st.markdown("---")
st.caption("RNGaaS Control Panel v1.0 | Built with Streamlit")
