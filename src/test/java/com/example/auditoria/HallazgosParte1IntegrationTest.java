package com.example.auditoria;

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

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@DisplayName("Pruebas de Integración de los Endpoints de la Parte 1")
class HallazgosParte1IntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("Ciclo completo: registrar, iniciar remediación, fallar cierre inválido, cerrar y reabrir")
    void testCicloCompletoEndpoints() throws Exception {
        // 1. POST /api/hallazgos retorna 201 Created con UUID
        String bodyCrear = """
            {
                "titulo": "Contraseñas por defecto en servidor de pruebas",
                "descripcion": "El servidor QA usa credenciales por defecto del fabricante",
                "areaResponsable": "Infraestructura",
                "severidad": "ALTA",
                "fechaDeteccion": "2026-08-01"
            }
            """;

        MvcResult resultCrear = mockMvc.perform(post("/api/hallazgos")
                .contentType(MediaType.APPLICATION_JSON)
                .content(bodyCrear))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.hallazgoId").exists())
                .andReturn();

        JsonNode jsonCrear = objectMapper.readTree(resultCrear.getResponse().getContentAsString());
        String id = jsonCrear.get("hallazgoId").asText();
        assertDoesNotThrow(() -> UUID.fromString(id));

        // 2. PATCH .../cerrar sobre hallazgo ABIERTO (sin plan) debe fallar con 400
        mockMvc.perform(patch("/api/hallazgos/" + id + "/cerrar"))
                .andExpect(status().isBadRequest());

        // 3. PATCH .../iniciar-remediacion sobre hallazgo ABIERTO retorna 200 y estado EN_REMEDIACION
        String bodyPlan = """
            {
                "responsable": "Equipo de Infraestructura",
                "fechaLimite": "2026-08-20",
                "notas": "Rotar credenciales"
            }
            """;

        mockMvc.perform(patch("/api/hallazgos/" + id + "/iniciar-remediacion")
                .contentType(MediaType.APPLICATION_JSON)
                .content(bodyPlan))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.estado").value("EN_REMEDIACION"));

        // 4. Consultar por ID y verificar estado EN_REMEDIACION y datos del plan
        mockMvc.perform(get("/api/hallazgos/" + id))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(id))
                .andExpect(jsonPath("$.estado").value("EN_REMEDIACION"))
                .andExpect(jsonPath("$.planResponsable").value("Equipo de Infraestructura"))
                .andExpect(jsonPath("$.planFechaLimite").value("2026-08-20"));

        // 5. PATCH .../cerrar sobre hallazgo EN_REMEDIACION retorna 200 y estado CERRADO
        mockMvc.perform(patch("/api/hallazgos/" + id + "/cerrar"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.estado").value("CERRADO"));

        // 6. PATCH .../reabrir sobre hallazgo CERRADO retorna 200 y estado REABIERTO
        String bodyReabrir = """
            {
                "motivo": "El hallazgo reapareció tras el despliegue del hotfix"
            }
            """;

        mockMvc.perform(patch("/api/hallazgos/" + id + "/reabrir")
                .contentType(MediaType.APPLICATION_JSON)
                .content(bodyReabrir))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.estado").value("REABIERTO"));

        // 7. GET /api/hallazgos lista los hallazgos
        mockMvc.perform(get("/api/hallazgos"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray());
    }
}
