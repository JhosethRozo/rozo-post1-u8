package com.example.auditoria.domain;

import com.example.auditoria.domain.entity.HallazgoAuditoria;
import com.example.auditoria.domain.valueobject.EstadoHallazgo;
import com.example.auditoria.domain.valueobject.HallazgoId;
import com.example.auditoria.domain.valueobject.PlanRemediacion;
import com.example.auditoria.domain.valueobject.Severidad;
import com.example.auditoria.domain.valueobject.TransicionInvalidaException;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.util.List;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("Pruebas Unitarias del Círculo Entities (Dominio Puro sin Spring)")
class HallazgoAuditoriaDomainTest {

    @Test
    @DisplayName("Debe instanciarse y transicionar correctamente en el ciclo de vida válido")
    void testCicloDeVidaValido() {
        HallazgoAuditoria hallazgo = new HallazgoAuditoria(
            HallazgoId.nuevo(),
            "Vulnerabilidad en SSH",
            "Puerto 22 abierto",
            "Seguridad",
            Severidad.CRITICA,
            LocalDate.of(2026, 8, 1)
        );

        assertEquals(EstadoHallazgo.ABIERTO, hallazgo.getEstado());
        assertNull(hallazgo.getPlanRemediacion());
        assertNull(hallazgo.getFechaCierre());

        // ABIERTO -> EN_REMEDIACION
        PlanRemediacion plan = new PlanRemediacion("SecTeam", LocalDate.of(2026, 8, 20), "Cerrar puerto");
        EstadoHallazgo ant1 = hallazgo.iniciarRemediacion(plan);
        assertEquals(EstadoHallazgo.ABIERTO, ant1);
        assertEquals(EstadoHallazgo.EN_REMEDIACION, hallazgo.getEstado());
        assertNotNull(hallazgo.getPlanRemediacion());

        // EN_REMEDIACION -> CERRADO
        EstadoHallazgo ant2 = hallazgo.cerrar();
        assertEquals(EstadoHallazgo.EN_REMEDIACION, ant2);
        assertEquals(EstadoHallazgo.CERRADO, hallazgo.getEstado());
        assertNotNull(hallazgo.getFechaCierre());

        // CERRADO -> REABIERTO
        EstadoHallazgo ant3 = hallazgo.reabrir();
        assertEquals(EstadoHallazgo.CERRADO, ant3);
        assertEquals(EstadoHallazgo.REABIERTO, hallazgo.getEstado());
        assertNull(hallazgo.getFechaCierre());

        // REABIERTO -> EN_REMEDIACION
        PlanRemediacion plan2 = new PlanRemediacion("SecTeam", LocalDate.of(2026, 8, 30), "Nuevo parche");
        EstadoHallazgo ant4 = hallazgo.iniciarRemediacion(plan2);
        assertEquals(EstadoHallazgo.REABIERTO, ant4);
        assertEquals(EstadoHallazgo.EN_REMEDIACION, hallazgo.getEstado());
    }

    @Test
    @DisplayName("Debe fallar al intentar cerrar un hallazgo sin plan de remediación")
    void testCerrarSinPlanFalla() {
        HallazgoAuditoria hallazgo = new HallazgoAuditoria(
            HallazgoId.nuevo(),
            "Vulnerabilidad en DB",
            "Credenciales por defecto",
            "DBA",
            Severidad.ALTA,
            LocalDate.of(2026, 8, 5)
        );

        assertThrows(IllegalStateException.class, hallazgo::cerrar);
    }

    @Test
    @DisplayName("Debe fallar al intentar transiciones inválidas en la máquina de estados")
    void testTransicionesInvalidas() {
        HallazgoAuditoria hallazgo = new HallazgoAuditoria(
            HallazgoId.nuevo(),
            "Falta backup",
            "No hay política de respaldos",
            "Infraestructura",
            Severidad.MEDIA,
            LocalDate.of(2026, 8, 10)
        );

        // No se puede reabrir un hallazgo abierto
        assertThrows(TransicionInvalidaException.class, hallazgo::reabrir);
    }

    @Test
    @DisplayName("Verificar que domain/ no contiene imports de org.springframework ni jakarta.persistence")
    void testPurezaCirculoDomain() throws IOException {
        Path domainDir = Path.of("src", "main", "java", "com", "example", "auditoria", "domain");
        try (Stream<Path> paths = Files.walk(domainDir)) {
            List<Path> javaFiles = paths.filter(p -> p.toString().endsWith(".java")).toList();
            assertFalse(javaFiles.isEmpty(), "Deben existir archivos Java en domain/");

            for (Path javaFile : javaFiles) {
                List<String> lines = Files.readAllLines(javaFile);
                for (String line : lines) {
                    assertFalse(line.contains("import org.springframework"),
                        "Violación de Clean Architecture: import de Spring en " + javaFile + ": " + line);
                    assertFalse(line.contains("import jakarta.persistence"),
                        "Violación de Clean Architecture: import de JPA en " + javaFile + ": " + line);
                }
            }
        }
    }

    @Test
    @DisplayName("Verificar que usecase/ no contiene imports de org.springframework")
    void testPurezaCirculoUseCase() throws IOException {
        Path usecaseDir = Path.of("src", "main", "java", "com", "example", "auditoria", "usecase");
        try (Stream<Path> paths = Files.walk(usecaseDir)) {
            List<Path> javaFiles = paths.filter(p -> p.toString().endsWith(".java")).toList();
            assertFalse(javaFiles.isEmpty(), "Deben existir archivos Java en usecase/");

            for (Path javaFile : javaFiles) {
                List<String> lines = Files.readAllLines(javaFile);
                for (String line : lines) {
                    assertFalse(line.contains("import org.springframework"),
                        "Violación de Clean Architecture: import de Spring en " + javaFile + ": " + line);
                }
            }
        }
    }
}
