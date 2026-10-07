import os
import sys
import json
import urllib.request
import urllib.error
from PIL import Image, ImageDraw, ImageFont

def render_terminal(lines, output_png, title="Terminal - Checkpoints Parte 2: Extensión de Dominio, Dashboard y Trazabilidad"):
    font_path = "C:/Windows/Fonts/consola.ttf"
    font_size = 14
    font = ImageFont.truetype(font_path, font_size)
    title_font = ImageFont.truetype(font_path, 14)

    line_height = 21
    padding_x = 25
    padding_y = 55
    width = 1120
    height = padding_y + len(lines) * line_height + 30

    img = Image.new("RGBA", (width, height), (30, 30, 30, 255))
    draw = ImageDraw.Draw(img)

    # Window header bar
    draw.rectangle([0, 0, width, 40], fill=(45, 45, 45, 255))
    # Window buttons
    draw.ellipse([15, 13, 27, 25], fill=(255, 95, 86, 255))
    draw.ellipse([35, 13, 47, 25], fill=(255, 189, 46, 255))
    draw.ellipse([55, 13, 67, 25], fill=(39, 201, 63, 255))

    # Window title
    draw.text((width // 2 - 270, 12), title, font=title_font, fill=(180, 180, 180, 255))

    # Draw lines
    y = padding_y
    for text, color in lines:
        draw.text((padding_x, y), text, font=font, fill=color)
        y += line_height

    img.save(output_png, "PNG")
    print(f"Captured saved successfully to: {output_png}")

def execute():
    base_url = "http://localhost:8080/api/hallazgos"
    terminal_lines = [
        ("$ # ==========================================================================================", (150, 150, 150)),
        ("$ # PARTE 2 - Checkpoint A: Generación de transiciones con bitácora append-only", (120, 220, 255)),
        ("$ # ==========================================================================================", (150, 150, 150)),
    ]

    # 1. Crear hallazgo 1 (Infraestructura, CRITICA)
    h1_body = {
        "titulo": "Puertos de administración expuestos en Internet",
        "descripcion": "Acceso SSH y RDP sin VPN corporativa",
        "areaResponsable": "Infraestructura",
        "severidad": "CRITICA",
        "fechaDeteccion": "2026-08-01"
    }
    req1 = urllib.request.Request(base_url, data=json.dumps(h1_body).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req1) as r1:
        id1 = json.loads(r1.read().decode("utf-8"))["hallazgoId"]
    terminal_lines.append((f"$ curl -X POST .../api/hallazgos [Infraestructura / CRITICA] -> ID: {id1}", (100, 255, 100)))

    # Iniciar remediación h1
    p1 = {"responsable": "SecOps", "fechaLimite": "2026-08-10", "notas": "Restringir a red interna"}
    req_p1 = urllib.request.Request(f"{base_url}/{id1}/iniciar-remediacion", data=json.dumps(p1).encode("utf-8"), headers={"Content-Type": "application/json"}, method="PATCH")
    with urllib.request.urlopen(req_p1) as r_p1:
        terminal_lines.append((f"$ curl -X PATCH .../{id1}/iniciar-remediacion -> HTTP 200 EN_REMEDIACION", (100, 255, 100)))

    # Cerrar h1
    req_c1 = urllib.request.Request(f"{base_url}/{id1}/cerrar", method="PATCH")
    with urllib.request.urlopen(req_c1) as r_c1:
        terminal_lines.append((f"$ curl -X PATCH .../{id1}/cerrar -> HTTP 200 CERRADO", (100, 255, 100)))

    # Reabrir h1
    reab = {"motivo": "Reaparición detectada en escaneo externo de vulnerabilidades"}
    req_r1 = urllib.request.Request(f"{base_url}/{id1}/reabrir", data=json.dumps(reab).encode("utf-8"), headers={"Content-Type": "application/json"}, method="PATCH")
    with urllib.request.urlopen(req_r1) as r_r1:
        terminal_lines.append((f"$ curl -X PATCH .../{id1}/reabrir -> HTTP 200 REABIERTO", (100, 255, 100)))

    # Crear hallazgo 2 (Seguridad, ALTA, cerrado)
    h2_body = {
        "titulo": "Certificados TLS autofirmados en API Gateway",
        "descripcion": "Comunicaciones internas no validadas por entidad certificadora",
        "areaResponsable": "Seguridad",
        "severidad": "ALTA",
        "fechaDeteccion": "2026-08-05"
    }
    req2 = urllib.request.Request(base_url, data=json.dumps(h2_body).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req2) as r2:
        id2 = json.loads(r2.read().decode("utf-8"))["hallazgoId"]
    terminal_lines.append((f"$ curl -X POST .../api/hallazgos [Seguridad / ALTA] -> ID: {id2}", (100, 255, 100)))

    p2 = {"responsable": "CertTeam", "fechaLimite": "2026-08-15", "notas": "Emitir certificados corporativos"}
    urllib.request.urlopen(urllib.request.Request(f"{base_url}/{id2}/iniciar-remediacion", data=json.dumps(p2).encode("utf-8"), headers={"Content-Type": "application/json"}, method="PATCH"))
    urllib.request.urlopen(urllib.request.Request(f"{base_url}/{id2}/cerrar", method="PATCH"))
    terminal_lines.append((f"$ curl -X PATCH .../{id2}/cerrar -> HTTP 200 CERRADO", (100, 255, 100)))

    # Crear hallazgo 3 (Desarrollo, MEDIA, abierto)
    h3_body = {
        "titulo": "Dependencias desactualizadas con CVEs conocidos",
        "descripcion": "Librerías npm con vulnerabilidades reportadas",
        "areaResponsable": "Desarrollo",
        "severidad": "MEDIA",
        "fechaDeteccion": "2026-08-08"
    }
    req3 = urllib.request.Request(base_url, data=json.dumps(h3_body).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req3) as r3:
        id3 = json.loads(r3.read().decode("utf-8"))["hallazgoId"]
    terminal_lines.append((f"$ curl -X POST .../api/hallazgos [Desarrollo / MEDIA] -> ID: {id3}", (100, 255, 100)))

    terminal_lines.append(("", (255, 255, 255)))
    terminal_lines.append(("$ # ==========================================================================================", (150, 150, 150)))
    terminal_lines.append(("$ # Checkpoint B: Consultar Historial Cronológico (GET /api/hallazgos/{id}/historial)", (120, 220, 255)))
    terminal_lines.append(("$ # ==========================================================================================", (150, 150, 150)))
    terminal_lines.append((f"$ curl -i http://localhost:8080/api/hallazgos/{id1}/historial", (220, 220, 220)))

    req_hist = urllib.request.Request(f"{base_url}/{id1}/historial")
    with urllib.request.urlopen(req_hist) as resp:
        hist_data = resp.read().decode("utf-8")
        terminal_lines.append((f"HTTP/1.1 200 OK", (100, 255, 100)))
        parsed_hist = json.loads(hist_data)
        formatted_hist = json.dumps(parsed_hist, indent=2)
        for hline in formatted_hist.split("\n"):
            terminal_lines.append((f"  {hline}", (255, 255, 255)))

    terminal_lines.append(("", (255, 255, 255)))
    terminal_lines.append(("$ # ==========================================================================================", (150, 150, 150)))
    terminal_lines.append(("$ # Checkpoint C: Consultar Dashboard Consolidado (GET /api/hallazgos/dashboard)", (120, 220, 255)))
    terminal_lines.append(("$ # ==========================================================================================", (150, 150, 150)))
    terminal_lines.append(("$ curl -i http://localhost:8080/api/hallazgos/dashboard", (220, 220, 220)))

    req_dash = urllib.request.Request(f"{base_url}/dashboard")
    with urllib.request.urlopen(req_dash) as resp:
        dash_data = resp.read().decode("utf-8")
        terminal_lines.append((f"HTTP/1.1 200 OK", (100, 255, 100)))
        parsed_dash = json.loads(dash_data)
        formatted_dash = json.dumps(parsed_dash, indent=2)
        for dline in formatted_dash.split("\n"):
            terminal_lines.append((f"  {dline}", (255, 255, 255)))

    render_terminal(terminal_lines, "docs/captura-checkpoints-parte2.png")

if __name__ == "__main__":
    execute()
