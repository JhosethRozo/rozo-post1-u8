import sys
from PIL import Image, ImageDraw, ImageFont

def render_architecture():
    width = 1100
    height = 680
    img = Image.new("RGBA", (width, height), (24, 28, 36, 255))
    draw = ImageDraw.Draw(img)

    font_path = "C:/Windows/Fonts/consola.ttf"
    title_font = ImageFont.truetype(font_path, 20)
    subtitle_font = ImageFont.truetype(font_path, 13)
    box_title_font = ImageFont.truetype(font_path, 15)
    text_font = ImageFont.truetype(font_path, 12)

    # Title
    draw.text((30, 25), "ARQUITECTURA LIMPIA (CLEAN ARCHITECTURE) - AUDITORIA DE HALLAZGOS", font=title_font, fill=(255, 255, 255))
    draw.text((30, 52), "Regla de Dependencia: Las dependencias del codigo solo apuntan hacia adentro (hacia el Dominio)", font=subtitle_font, fill=(160, 174, 192))

    # Outer: Frameworks & Drivers
    draw.rounded_rectangle([30, 85, 1070, 640], radius=16, fill=(30, 41, 59, 255), outline=(71, 85, 105, 255), width=2)
    draw.text((50, 100), "[4] FRAMEWORKS & DRIVERS (Spring Boot 3.3.4, JPA/Hibernate, Base de Datos H2)", font=box_title_font, fill=(148, 163, 184))
    draw.text((50, 122), "• AuditoriaHallazgosApplication.java  • AuditoriaConfiguration.java  • H2 In-Memory DB (auditoria_db)", font=text_font, fill=(203, 213, 225))

    # Third: Interface Adapters
    draw.rounded_rectangle([55, 155, 1045, 615], radius=14, fill=(15, 23, 42, 255), outline=(14, 165, 233, 255), width=2)
    draw.text((75, 170), "[3] INTERFACE ADAPTERS (adapter/in/web y adapter/out/persistence)", font=box_title_font, fill=(56, 189, 248))
    
    # In Web Box
    draw.rounded_rectangle([75, 200, 530, 290], radius=8, fill=(30, 41, 59, 255), outline=(56, 189, 248, 255), width=1)
    draw.text((85, 210), "Controlador Web (REST API):", font=text_font, fill=(56, 189, 248))
    draw.text((85, 230), "• HallazgoController.java (/api/hallazgos)", font=text_font, fill=(241, 245, 249))
    draw.text((85, 250), "• DTOs: RegistrarReq, IniciarRemReq, ReabrirReq, HallazgoResp", font=text_font, fill=(203, 213, 225))
    draw.text((85, 270), "• GlobalExceptionHandler.java (400 Bad Request, 404 Not Found)", font=text_font, fill=(203, 213, 225))

    # Out Persistence Box
    draw.rounded_rectangle([550, 200, 1025, 290], radius=8, fill=(30, 41, 59, 255), outline=(56, 189, 248, 255), width=1)
    draw.text((560, 210), "Adaptadores de Persistencia (JPA + Append-Only):", font=text_font, fill=(56, 189, 248))
    draw.text((560, 230), "• HallazgoRepositoryAdapter -> HallazgoJpaRepository, HallazgoJpaEntity", font=text_font, fill=(241, 245, 249))
    draw.text((560, 250), "• HistorialAuditoriaAdapter -> HistorialCambioEstadoJpaRepo/Entity", font=text_font, fill=(241, 245, 249))
    draw.text((560, 270), "• Proyecciones JPQL/Native: contarPorSeveridad, contarPorEstado, avgDias", font=text_font, fill=(203, 213, 225))

    # Second: Use Cases
    draw.rounded_rectangle([75, 310, 1025, 595], radius=12, fill=(24, 24, 27, 255), outline=(34, 197, 94, 255), width=2)
    draw.text((95, 325), "[2] USE CASES (usecase/ - Casos de Uso y Puertos de Salida - Puro Java sin Spring)", font=box_title_font, fill=(74, 222, 128))
    draw.text((95, 350), "• Casos de Uso: Registrar, IniciarRemediacion, Cerrar, Reabrir, Consultar, Dashboard, Historial", font=text_font, fill=(241, 245, 249))
    draw.text((95, 370), "• Puertos (Interfaces DIP): HallazgoRepositoryPort, HistorialAuditoriaPort", font=text_font, fill=(203, 213, 225))
    draw.text((95, 390), "• Vistas/Records: ConteoCategoria, PromedioCategoria, DashboardAuditoriaView, CambioEstadoView", font=text_font, fill=(203, 213, 225))

    # First: Entities
    draw.rounded_rectangle([95, 420, 1005, 575], radius=10, fill=(39, 39, 42, 255), outline=(234, 179, 8, 255), width=2)
    draw.text((115, 435), "[1] ENTITIES / DOMAIN (domain/ - Nucleo Empresarial Puro sin Frameworks)", font=box_title_font, fill=(250, 204, 21))
    draw.text((115, 460), "• Aggregate Root: HallazgoAuditoria (gestiona invariantes y ciclo de vida transaccional)", font=text_font, fill=(255, 255, 255))
    draw.text((115, 480), "• Value Objects: HallazgoId (UUID tipado), PlanRemediacion (Inmutable embebido)", font=text_font, fill=(244, 244, 245))
    draw.text((115, 500), "• Enums: EstadoHallazgo (Maquina de estados: puedeTransicionarA), Severidad (Simple)", font=text_font, fill=(244, 244, 245))
    draw.text((115, 520), "• Excepcion de Dominio: TransicionInvalidaException", font=text_font, fill=(244, 244, 245))
    draw.text((115, 545), ">>> Invariante: ABIERTO -> EN_REMEDIACION -> CERRADO -> REABIERTO -> EN_REMEDIACION <<<", font=text_font, fill=(250, 204, 21))

    img.save("docs/diagrama-arquitectura.png", "PNG")
    print("Architecture diagram saved as PNG")

if __name__ == "__main__":
    render_architecture()
