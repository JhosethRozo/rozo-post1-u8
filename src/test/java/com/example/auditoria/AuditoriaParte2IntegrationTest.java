package com.example.auditoria;

import com.example.auditoria.adapter.out.persistence.HistorialCambioEstadoJpaRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@DisplayName("Pruebas de Integración de la Parte 2: Dashboard y Bitácora de Trazabilidad")
class AuditoriaParte2IntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private HistorialCambioEstadoJpaRepository historialRepo;

    @Test
    @DisplayName("Debe registrar transiciones en bitácora append-only y consultar historial cronológico")
    void testHistorialTrazabilidad() throws Exception {
        long historialInicial = historialRepo.count();

        // 1. Crear hallazgo
        String bodyCrear = """
            {
                "titulo": "Fuga de memoria en microservicio de reportes",
                "descripcion": "El pod se reinicia cada 4 horas",
                "areaResponsable": "Desarrollo",
                "severidad": "CRITICA",
                "fechaDeteccion": "2026-08-01"
            }
            """;

        MvcResult resCrear = mockMvc.perform(post("/api/hallazgos")
                .contentType(MediaType.APPLICATION_JSON)
                .content(bodyCrear))
                .andExpect(status().isCreated())
                .andReturn();

        String id = objectMapper.readTree(resCrear.getResponse().getContentAsString()).get("hallazgoId").asText();

        // Al crear no hay transiciones previas
        assertEquals(historialInicial, historialRepo.count());

        // 2. Iniciar remediación (Transición 1: ABIERTO -> EN_REMEDIACION)
        String bodyPlan = """
            {
                "responsable": "Equipo Backend",
                "fechaLimite": "2026-08-15",
                "notas": "Optimizar streams y cerrar conexiones"
            }
            """;
        mockMvc.perform(patch("/api/hallazgos/" + id + "/iniciar-remediacion")
                .contentType(MediaType.APPLICATION_JSON)
                .content(bodyPlan))
                .andExpect(status().isOk());

        assertEquals(historialInicial + 1, historialRepo.count(), "Debe insertar 1 registro en bitacora");

        // 3. Cerrar hallazgo (Transición 2: EN_REMEDIACION -> CERRADO)
        mockMvc.perform(patch("/api/hallazgos/" + id + "/cerrar"))
                .andExpect(status().isOk());

        assertEquals(historialInicial + 2, historialRepo.count(), "Debe insertar 1 registro adicional");

        // 4. Reabrir hallazgo (Transición 3: CERRADO -> REABIERTO)
        String bodyReabrir = """
            {
                "motivo": "Reincidencia en pruebas de carga"
            }
            """;
        mockMvc.perform(patch("/api/hallazgos/" + id + "/reabrir")
                .contentType(MediaType.APPLICATION_JSON)
                .content(bodyReabrir))
                .andExpect(status().isOk());

        assertEquals(historialInicial + 3, historialRepo.count(), "Debe insertar 1 registro adicional");

        // 5. Consultar historial cronológico GET /api/hallazgos/{id}/historial
        MvcResult resHistorial = mockMvc.perform(get("/api/hallazgos/" + id + "/historial"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray())
                .andReturn();

        JsonNode items = objectMapper.readTree(resHistorial.getResponse().getContentAsString());
        assertEquals(3, items.size());

        // Verificar secuencia cronológica
        assertEquals("ABIERTO", items.get(0).get("estadoAnterior").asText());
        assertEquals("EN_REMEDIACION", items.get(0).get("estadoNuevo").asText());

        assertEquals("EN_REMEDIACION", items.get(1).get("estadoAnterior").asText());
        assertEquals("CERRADO", items.get(1).get("estadoNuevo").asText());

        assertEquals("CERRADO", items.get(2).get("estadoAnterior").asText());
        assertEquals("REABIERTO", items.get(2).get("estadoNuevo").asText());
        assertEquals("Reincidencia en pruebas de carga", items.get(2).get("motivo").asText());
    }

    @Test
    @DisplayName("Debe consultar dashboard consolidado con conteos y promedio de días")
    void testDashboardConsolidado() throws Exception {
        // Crear y cerrar un hallazgo para generar métricas de promedio
        String bodyCrear = """
            {
                "titulo": "Puerto inseguro 8080 abierto",
                "descripcion": "Falta SSL en frontend",
                "areaResponsable": "Seguridad",
                "severidad": "MEDIA",
                "fechaDeteccion": "2026-08-01"
            }
            """;
        MvcResult resCrear = mockMvc.perform(post("/api/hallazgos")
                .contentType(MediaType.APPLICATION_JSON)
                .content(bodyCrear))
                .andExpect(status().isCreated())
                .andReturn();

        String id = objectMapper.readTree(resCrear.getResponse().getContentAsString()).get("hallazgoId").asText();

        mockMvc.perform(patch("/api/hallazgos/" + id + "/iniciar-remediacion")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"responsable":"SecAdmin","fechaLimite":"2026-08-10","notas":"Certificado instalado"}
                    """))
                .andExpect(status().isOk());

        mockMvc.perform(patch("/api/hallazgos/" + id + "/cerrar"))
                .andExpect(status().isOk());

        // Consultar Dashboard GET /api/hallazgos/dashboard
        mockMvc.perform(get("/api/hallazgos/dashboard"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.porSeveridad").isArray())
                .andExpect(jsonPath("$.porEstado").isArray())
                .andExpect(jsonPath("$.promedioDiasCierrePorArea").isArray());
    }
}
