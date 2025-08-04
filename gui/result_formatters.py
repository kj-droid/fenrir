# gui/result_formatters.py

def format_port_scan(data):
    """Formats port scanner results into a readable string."""
    # FIX: Check if data is a dictionary before processing
    if not isinstance(data, dict) or not data:
        return str(data) # Return the string message directly

    output = []
    for target, host_data in data.items():
        output.append(f"Target: {target}\n" + "="*20)
        ports = host_data.get('ports', [])
        if not ports:
            output.append("No open ports found.")
            continue
        for port_info in ports:
            product = port_info.get('product', 'unknown')
            version = port_info.get('version', '')
            name = port_info.get('name', 'unknown')
            output.append(f"  Port: {port_info['port']}/{port_info['state']}")
            output.append(f"    Service: {name}")
            output.append(f"    Product: {product} {version}\n")
    return "\n".join(output)

def format_vulnerabilities(data):
    """Formats vulnerability identifier results into a readable string."""
    # FIX: Check if data is a dictionary before processing
    if not isinstance(data, dict) or not data:
        return str(data)

    output = []
    for service_key, cve_list in data.items():
        output.append(f"Service/Term: {service_key}\n" + "="*20)
        for cve in cve_list:
            output.append(f"  CVE ID: {cve.get('cve_id')}")
            output.append(f"    Severity: {cve.get('severity', 'N/A')} (Score: {cve.get('cvss_v3_score', 'N/A')})")
            output.append(f"    Description: {cve.get('description', 'No description available.')}\n")
    return "\n".join(output)

def format_exploits(data):
    """Formats exploit finder results into a readable string."""
    # FIX: Check if data is a dictionary before processing
    if not isinstance(data, dict) or not data:
        return str(data)
    
    output = []
    for key, exploit_list in data.items():
        output.append(f"Reference: {key}\n" + "="*20)
        for exploit in exploit_list:
            output.append(f"  EDB-ID: {exploit.get('EDB-ID')}")
            output.append(f"    Description: {exploit.get('Title')}")
            output.append(f"    Type: {exploit.get('Type')}  |  Platform: {exploit.get('Platform')}")
            output.append(f"    Path: {exploit.get('Path')}\n")
    return "\n".join(output)

def format_default(data):
    """A default formatter that pretty-prints JSON for any other module."""
    import json
    if isinstance(data, (dict, list)):
        return json.dumps(data, indent=4)
    return str(data)

# Maps module names to their specific formatting function
RESULT_FORMATTERS = {
    "port_scanner": format_port_scan,
    "vulnerability_identifier": format_vulnerabilities,
    "exploit_finder": format_exploits,
}
