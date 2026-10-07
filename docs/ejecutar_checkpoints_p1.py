import os
import sys
import json
import urllib.request
import urllib.error
from PIL import Image, ImageDraw, ImageFont

def render_terminal(lines, output_png, title="Terminal - Checkpoints Parte 1: Clean Architecture (Unidad 8)"):
    font_path = "C:/Windows/Fonts/consola.ttf"
    font_size = 15
    font = ImageFont.truetype(font_path, font_size)
    title_font = ImageFont.truetype(font_path, 14)

    line_height = 22
    padding_x = 25
    padding_y = 55
    width = 1100
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
    draw.text((width // 2 - 240, 12), title, font=title_font, fill=(180, 180, 180, 255))

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
        ("$ # =====================================================================", (150, 150, 150)),
        ("$ # Checkpoint 1: Registrar un nuevo hallazgo de auditoría (HTTP POST /api/hallazgos)", (120, 220, 255)),
        ("$ # =====================================================================", (150, 150, 150)),
        ("$ curl -i -X POST http://localhost:8080/api/hallazgos \\", (220, 220, 220)),
        ("    -H 'Content-Type: application/json' \\", (220, 220, 220)),
        ("    -d '{\"titulo\":\"Contraseñas por defecto en servidor de pruebas\",\"areaResponsable\":\"Infraestructura\",\"severidad\":\"ALTA\",...}'", (220, 220, 220)),
    ]

    # 1. POST
    req_body = {
        "titulo": "Contraseñas por defecto en servidor de pruebas",
        "descripcion": "El servidor QA usa credenciales por defecto del fabricante",
        "areaResponsable": "Infraestructura",
        "severidad": "ALTA",
        "fechaDeteccion": "2026-08-01"
    }
    req = urllib.request.Request(base_url, data=json.dumps(req_body).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        res_data = resp.read().decode("utf-8")
        terminal_lines.append((f"HTTP/1.1 201 Created", (100, 255, 100)))
        terminal_lines.append((f"Content-Type: application/json", (180, 180, 180)))
        terminal_lines.append((f"Response Body: {res_data}", (255, 255, 255)))
        hallazgo_id = json.loads(res_data)["hallazgoId"]

    terminal_lines.append(("", (255, 255, 255)))
    terminal_lines.append(("$ # =====================================================================", (150, 150, 150)))
    terminal_lines.append((f"$ # Checkpoint 2: Iniciar remediación (ABIERTO -> EN_REMEDIACION con PlanRemediacion)", (120, 220, 255)))
    terminal_lines.append(("$ # =====================================================================", (150, 150, 150)))
    terminal_lines.append((f"$ curl -i -X PATCH http://localhost:8080/api/hallazgos/{hallazgo_id}/iniciar-remediacion \\", (220, 220, 220)))
    terminal_lines.append(("    -d '{\"responsable\":\"Equipo de Infraestructura\",\"fechaLimite\":\"2026-08-20\",\"notas\":\"Rotar credenciales\"}'", (220, 220, 220)))

    plan_body = {
        "responsable": "Equipo de Infraestructura",
        "fechaLimite": "2026-08-20",
        "notas": "Rotar credenciales"
    }
    req = urllib.request.Request(f"{base_url}/{hallazgo_id}/iniciar-remediacion", data=json.dumps(plan_body).encode("utf-8"), headers={"Content-Type": "application/json"}, method="PATCH")
    with urllib.request.urlopen(req) as resp:
        res_data = resp.read().decode("utf-8")
        terminal_lines.append((f"HTTP/1.1 200 OK", (100, 255, 100)))
        terminal_lines.append((f"Response Body: {res_data}", (255, 255, 255)))

    terminal_lines.append(("", (255, 255, 255)))
    terminal_lines.append(("$ # =====================================================================", (150, 150, 150)))
    terminal_lines.append(("$ # Checkpoint 3: Intentar cerrar hallazgo ABIERTO sin plan (Debe fallar con 400 Bad Request)", (120, 220, 255)))
    terminal_lines.append(("$ # =====================================================================", (150, 150, 150)))

    req_body2 = {
        "titulo": "Servidor sin backups automatizados",
        "descripcion": "No se encontraron politicas de respaldo",
        "areaResponsable": "TI",
        "severidad": "MEDIA",
        "fechaDeteccion": "2026-08-05"
    }
    req2 = urllib.request.Request(base_url, data=json.dumps(req_body2).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req2) as resp2:
        id_abierto = json.loads(resp2.read().decode("utf-8"))["hallazgoId"]

    terminal_lines.append((f"$ curl -i -X PATCH http://localhost:8080/api/hallazgos/{id_abierto}/cerrar", (220, 220, 220)))
    try:
        req_err = urllib.request.Request(f"{base_url}/{id_abierto}/cerrar", method="PATCH")
        with urllib.request.urlopen(req_err) as r:
            pass
    except urllib.error.HTTPError as e:
        err_res = e.read().decode("utf-8")
        terminal_lines.append((f"HTTP/1.1 {e.code} Bad Request", (255, 100, 100)))
        terminal_lines.append((f"Response Body: {err_res}", (255, 180, 180)))

    terminal_lines.append(("", (255, 255, 255)))
    terminal_lines.append(("$ # =====================================================================", (150, 150, 150)))
    terminal_lines.append(("$ # Checkpoint 4: Cerrar hallazgo tras remediación válida (EN_REMEDIACION -> CERRADO)", (120, 220, 255)))
    terminal_lines.append(("$ # =====================================================================", (150, 150, 150)))
    terminal_lines.append((f"$ curl -i -X PATCH http://localhost:8080/api/hallazgos/{hallazgo_id}/cerrar", (220, 220, 220)))
    req_close = urllib.request.Request(f"{base_url}/{hallazgo_id}/cerrar", method="PATCH")
    with urllib.request.urlopen(req_close) as resp:
        res_data = resp.read().decode("utf-8")
        terminal_lines.append((f"HTTP/1.1 200 OK", (100, 255, 100)))
        terminal_lines.append((f"Response Body: {res_data}", (255, 255, 255)))

    terminal_lines.append(("", (255, 255, 255)))
    terminal_lines.append(("$ # =====================================================================", (150, 150, 150)))
    terminal_lines.append(("$ # Checkpoint 5: Reabrir hallazgo CERRADO -> REABIERTO", (120, 220, 255)))
    terminal_lines.append(("$ # =====================================================================", (150, 150, 150)))
    terminal_lines.append((f"$ curl -i -X PATCH http://localhost:8080/api/hallazgos/{hallazgo_id}/reabrir \\", (220, 220, 220)))
    terminal_lines.append(("    -d '{\"motivo\":\"Reaparición del hallazgo tras actualización\"}'", (220, 220, 220)))
    reabrir_body = {"motivo": "Reaparición del hallazgo tras actualización"}
    req_reabrir = urllib.request.Request(f"{base_url}/{hallazgo_id}/reabrir", data=json.dumps(reabrir_body).encode("utf-8"), headers={"Content-Type": "application/json"}, method="PATCH")
    with urllib.request.urlopen(req_reabrir) as resp:
        res_data = resp.read().decode("utf-8")
        terminal_lines.append((f"HTTP/1.1 200 OK", (100, 255, 100)))
        terminal_lines.append((f"Response Body: {res_data}", (255, 255, 255)))

    terminal_lines.append(("", (255, 255, 255)))
    terminal_lines.append(("$ # =====================================================================", (150, 150, 150)))
    terminal_lines.append(("$ # Checkpoint 6: Consultar hallazgo por ID y listar todos los hallazgos", (120, 220, 255)))
    terminal_lines.append(("$ # =====================================================================", (150, 150, 150)))
    terminal_lines.append((f"$ curl -i http://localhost:8080/api/hallazgos/{hallazgo_id}", (220, 220, 220)))
    req_get = urllib.request.Request(f"{base_url}/{hallazgo_id}")
    with urllib.request.urlopen(req_get) as resp:
        res_data = resp.read().decode("utf-8")
        terminal_lines.append((f"HTTP/1.1 200 OK", (100, 255, 100)))
        terminal_lines.append((f"Response Body: {res_data}", (255, 255, 255)))

    render_terminal(terminal_lines, "docs/captura-checkpoints-parte1.png")

if __name__ == "__main__":
    execute()
