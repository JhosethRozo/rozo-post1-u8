package com.example.auditoria.adapter.out.persistence;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface HallazgoJpaRepository extends JpaRepository<HallazgoJpaEntity, String> {

    @Query("SELECT h.severidad AS categoria, COUNT(h) AS total FROM HallazgoJpaEntity h GROUP BY h.severidad")
    List<ConteoProjection> contarPorSeveridad();

    @Query("SELECT h.estado AS categoria, COUNT(h) AS total FROM HallazgoJpaEntity h GROUP BY h.estado")
    List<ConteoProjection> contarPorEstado();

    @Query(value = "SELECT h.area_responsable AS categoria, " +
           "AVG(DATEDIFF('DAY', h.fecha_deteccion, h.fecha_cierre)) AS promedio " +
           "FROM hallazgos h WHERE h.estado = 'CERRADO' GROUP BY h.area_responsable", nativeQuery = true)
    List<PromedioProjection> promedioDiasCierrePorArea();

    interface ConteoProjection {
        String getCategoria();
        Long getTotal();
    }

    interface PromedioProjection {
        String getCategoria();
        Double getPromedio();
    }
}
